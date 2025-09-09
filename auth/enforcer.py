import casbin

class CasbinEnforcer:
    def __init__(self, model_path: str, policy_path: str):
        self.enforcer = casbin.Enforcer(model_path, policy_path)

    def add_policy(self, sub: str, obj: str, act: str) -> bool:
        return self.enforcer.add_policy(sub, obj, act)

    def remove_policy(self, sub: str, obj: str, act: str) -> bool:
        return self.enforcer.remove_policy(sub, obj, act)

    def enforce(self, sub: str, obj: str, act: str) -> bool:
        return self.enforcer.enforce(sub, obj, act)

    def get_policies(self):
        return self.enforcer.get_policy()

    def save_policy(self):
        self.enforcer.save_policy()


if __name__ == "__main__":
    # Simple local demo kept for manual testing
    e = CasbinEnforcer("auth/models/rbac_model.conf", "auth/policies/rbac_policy.csv")
    print(e.enforce("alice", "data1", "read"))
    print(e.get_policies())