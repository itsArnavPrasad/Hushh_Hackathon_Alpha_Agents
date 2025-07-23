from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.shopping import HushhShoppingAgent
from hushh_mcp.constants import ConsentScope

USER_ID = "arnav"
AGENT_ID = "agent_shopper"
SCOPE = ConsentScope.VAULT_READ_EMAIL

def main():
    # Issue a consent token for the user and agent
    token_obj = issue_token(USER_ID, AGENT_ID, SCOPE)
    print(f"Issued token: {token_obj.token}")

    # Instantiate the shopping agent
    shopping_agent = HushhShoppingAgent(agent_id=AGENT_ID)

    # Use the agent to search for deals
    try:
        deals = shopping_agent.search_deals(USER_ID, token_obj.token)
        print("Personalized deals:")
        for deal in deals:
            print(f"- {deal}")
    except PermissionError as e:
        print(f"Permission error: {e}")

if __name__ == "__main__":
    main()
