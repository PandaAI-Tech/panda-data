


if __name__ == "__main__":
    from panda_tools.credential import CredentialManager
    from panda_tools.registry import ToolRegistry

    CredentialManager.init_from_env()
    registry = ToolRegistry()
    tools = registry.get_all_tools()
    result = registry.call_tool("get_market_data", start_date="20250101", end_date="20250110", symbol="000001.SZ")
    print(result)