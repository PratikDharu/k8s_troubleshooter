import re


class RuleEngine:
    def analyze(self, text: str):
        normalized = text.lower()

        if "crashloopbackoff" in normalized or "back-off restarting failed container" in normalized:
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

        if "imagepullbackoff" in normalized or "failed to pull image" in normalized:
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

        if "oomkilled" in normalized or "out of memory" in normalized:
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

        if re.search(r"liveness probe|readiness probe|probe failed", normalized):
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

        if re.search(r"insufficient (cpu|memory)|0/\d+ nodes are available", normalized):
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

        return {
            "problem": "Unknown",
            "explanation": "No predefined Kubernetes issue detected from the supplied diagnostics.",
            "confidence": 30,
            "commands": [
                "kubectl describe pod",
                "kubectl logs",
                "kubectl get events",
            ],
        }
