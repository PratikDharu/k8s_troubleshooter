import os
import re

try:
    import requests
except ImportError:  # pragma: no cover - exercised in minimal environments
    requests = None


class RuleEngine:
    def _extract_event_fields(self, text: str):
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return {}

        event_lines = []
        for line in lines:
            if line.startswith("Events:"):
                continue
            if line.startswith("Type") and "Reason" in line:
                continue
            if line.startswith("----"):
                continue
            if line.startswith("Warning") or line.startswith("Normal"):
                event_lines.append(line)

        if not event_lines:
            return {}

        message_parts = []
        for line in event_lines:
            parts = re.split(r"\s{2,}", line)
            if len(parts) >= 3:
                message_parts.append(parts[-1])

        combined_message = " ".join(message_parts)
        return {"event_message": combined_message}

    def _llm_fallback(self, text: str):
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        model = os.getenv("OPENAI_MODEL") or os.getenv("OLLAMA_MODEL") or "gpt-4o-mini"
        ollama_api_base = os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434/api")

        if requests is None:
            return None

        if api_key:
            endpoint = f"{(api_base or 'https://api.openai.com/v1').rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a Kubernetes troubleshooting assistant. Given Kubernetes error text, "
                            "identify the likely issue, explain briefly what it means, and suggest 3 useful "
                            "kubectl commands. Return JSON with keys: problem, explanation, confidence, commands."
                        ),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                "temperature": 0.2,
            }
        else:
            endpoint = f"{ollama_api_base.rstrip('/')}/chat"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a Kubernetes troubleshooting assistant. Given Kubernetes error text, "
                            "identify the likely issue, explain briefly what it means, and suggest 3 useful "
                            "kubectl commands. Return JSON with keys: problem, explanation, confidence, commands."
                        ),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                "stream": False,
            }

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            payload = response.json()
            if api_key:
                return payload["choices"][0]["message"]["content"]
            return payload["message"]["content"]
        except Exception:
            return None

    def analyze(self, text: str):
        normalized = text.lower()
        structured = self._extract_event_fields(text)
        event_message = structured.get("event_message", "")
        combined = f"{normalized}\n{event_message.lower()}"

        if "crashloopbackoff" in combined or "back-off restarting failed container" in combined:
            return {
                "problem": "CrashLoopBackOff",
                "explanation": (
                    "The container is repeatedly restarting, which usually points to an application "
                    "startup failure or a configuration issue. Check the pod logs and recent events."
                ),
                "confidence": 95,
                "commands": [
                    "kubectl logs <pod>",
                    "kubectl describe pod <pod>",
                    "kubectl get events",
                ],
            }

        if re.search(r"imagepullbackoff|errimagepull|failed to pull image|back-off pulling image", combined):
            return {
                "problem": "ImagePullBackOff",
                "explanation": (
                    "Kubernetes could not pull the container image, often due to an invalid image name, "
                    "missing credentials, or a registry access issue."
                ),
                "confidence": 98,
                "commands": [
                    "kubectl describe pod <pod>",
                    "kubectl get secret",
                    "kubectl get serviceaccount",
                ],
            }

        if "oomkilled" in combined or "out of memory" in combined:
            return {
                "problem": "OOMKilled",
                "explanation": (
                    "The container exceeded its memory limit and was terminated by the kernel. "
                    "Increase memory requests/limits or optimize the workload."
                ),
                "confidence": 97,
                "commands": [
                    "kubectl top pod",
                    "kubectl describe pod <pod>",
                    "kubectl edit deployment <name>",
                ],
            }

        if re.search(r"liveness probe|readiness probe|probe failed", combined):
            return {
                "problem": "ProbeFailure",
                "explanation": (
                    "A readiness or liveness probe failed, which means the application is not responding "
                    "to health checks and the pod may be restarted or marked unhealthy."
                ),
                "confidence": 90,
                "commands": [
                    "kubectl describe pod <pod>",
                    "kubectl logs <pod>",
                    "kubectl get events",
                ],
            }

        if re.search(r"insufficient (cpu|memory)|0/\d+ nodes are available|pending|failedscheduling", combined):
            return {
                "problem": "SchedulingFailure",
                "explanation": (
                    "The workload could not be scheduled because the cluster does not currently have enough "
                    "resources available for the requested node placement."
                ),
                "confidence": 92,
                "commands": [
                    "kubectl describe pod <pod>",
                    "kubectl get nodes",
                    "kubectl top nodes",
                ],
            }

        if re.search(r"failed mount|mountvolume|failed to mount|volume .* failed", combined):
            return {
                "problem": "FailedMount",
                "explanation": (
                    "A volume or persistent storage mount failed, which often points to a misconfigured "
                    "secret, config map, PVC, or storage class."
                ),
                "confidence": 91,
                "commands": [
                    "kubectl describe pod <pod>",
                    "kubectl get pvc",
                    "kubectl get pv",
                ],
            }

        if re.search(r"no such host|dns|lookup .*svc\.cluster\.local|service unavailable", combined):
            return {
                "problem": "DNSResolutionFailure",
                "explanation": (
                    "The pod could not resolve a Kubernetes service or DNS name, which may indicate a "
                    "service discovery issue, DNS misconfiguration, or missing endpoints."
                ),
                "confidence": 89,
                "commands": [
                    "kubectl get svc",
                    "kubectl get endpoints",
                    "kubectl describe pod <pod>",
                ],
            }

        if re.search(r"forbidden|unauthorized|rbac|forbidden: user", combined):
            return {
                "problem": "RBACOrPermissionIssue",
                "explanation": (
                    "The request was denied by Kubernetes authorization, often because the service account, "
                    "user, or role lacks the required permissions."
                ),
                "confidence": 88,
                "commands": [
                    "kubectl auth can-i <verb> <resource>",
                    "kubectl describe rolebinding",
                    "kubectl describe clusterrolebinding",
                ],
            }

        fallback = self._llm_fallback(text)
        if fallback:
            try:
                import json

                parsed = json.loads(fallback)
                return {
                    "problem": parsed.get("problem", "Unknown"),
                    "explanation": parsed.get("explanation", "The model could not produce a clear explanation."),
                    "confidence": parsed.get("confidence", 60),
                    "commands": parsed.get("commands", ["kubectl describe pod", "kubectl logs", "kubectl get events"]),
                }
            except Exception:
                pass

        return {
            "problem": "Unknown",
            "explanation": (
                "No predefined Kubernetes issue matched the supplied diagnostics. Try providing more "
                "detail such as the pod event, container status, or error message."
            ),
            "confidence": 30,
            "commands": [
                "kubectl describe pod",
                "kubectl logs",
                "kubectl get events",
            ],
        }
