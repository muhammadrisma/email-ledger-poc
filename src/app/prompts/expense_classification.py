"""
Expense classification prompt template.
"""

EXPENSE_CLASSIFICATION_PROMPT = """
Classify this expense into one of the following categories:
{categories}

Consider the vendor name, description, amount, and email content to determine the most appropriate category.

Categories explained:
- meals_and_entertainment: Food, restaurants, entertainment
- transport: Uber, Lyft, gas, parking, public transport
- saas_subscriptions: Software subscriptions, online services
- travel: Flights, hotels, travel expenses
- office_supplies: Office materials, equipment
- utilities: Electricity, water, internet, phone bills
- insurance: Insurance payments
- professional_services: Legal, consulting, professional fees
- marketing: Advertising, marketing expenses
- other: Anything that doesn't fit above categories

Return the result in JSON format:
{{
    "category": "category_name"
}}

Content to classify:
{content}
""" 