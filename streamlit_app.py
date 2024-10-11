import streamlit as st
from openai import OpenAI

# Set up the title and description.
st.title("🍜 Cooking Assistant")
st.write(
    "Welcome to your personal cooking assistant! "
    "This app will help you decide what to cook with the ingredients you have, "
    "focusing on Asian cuisine. Just let me know what you feel like eating today, "
    "and I'll suggest some dishes!"
)

# Access the OpenAI API key from the secrets configuration.
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Initialize session state for storing ingredients and selected dishes.
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []

if "selected_dish" not in st.session_state:
    st.session_state.selected_dish = None

# Input ingredients.
st.subheader("Add Your Available Ingredients")
new_ingredient = st.text_input("Enter an ingredient:")
if st.button("Add Ingredient"):
    if new_ingredient and new_ingredient not in st.session_state.ingredients:
        st.session_state.ingredients.append(new_ingredient)
        st.success(f"Added {new_ingredient} to your list of ingredients.")
    elif new_ingredient in st.session_state.ingredients:
        st.warning(f"{new_ingredient} is already in your list.")
    new_ingredient = ""  # Clear input field.

# Display current list of ingredients.
st.subheader("Your Ingredients")
if st.session_state.ingredients:
    st.write(", ".join(st.session_state.ingredients))
else:
    st.write("No ingredients added yet.")

# Ask the user what they want to eat today.
st.subheader("What do you feel like eating today?")
cuisine_preference = st.text_input("Enter your desired cuisine (e.g., 'Asian cuisine'): ")

# Generate food options based on user input.
if cuisine_preference and st.button("Get Cooking Options"):
    prompt = (
        f"I have the following ingredients: {', '.join(st.session_state.ingredients)}. "
        f"I would like to cook something in {cuisine_preference}. "
        "What are some possible dishes I can make?"
    )

    # Generate a list of possible dishes.
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful cooking assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=100,
        n=5,
        stop=None,
        temperature=0.7,
    )

    # Display possible options.
    if response.choices:
        # Extract the content from each choice's message.
        st.session_state.options = [choice.message.content.strip() for choice in response.choices]
        st.write("Here are some dishes you could make:")
        for i, option in enumerate(st.session_state.options):
            st.write(f"{i + 1}. {option}")
    else:
        st.write("No options were generated. Please try again.")

# Let the user select a dish from the generated options.
st.subheader("Choose a Dish")
if "options" in st.session_state:
    selected_index = st.selectbox("Select a dish from the options:", list(range(len(st.session_state.options))))
    if st.button("Get Recipe"):
        st.session_state.selected_dish = st.session_state.options[selected_index]

# Generate a recipe for the selected dish.
if st.session_state.selected_dish:
    st.subheader(f"Recipe for {st.session_state.selected_dish}")
    prompt = f"Provide a step-by-step recipe for {st.session_state.selected_dish} using the following ingredients: {', '.join(st.session_state.ingredients)}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful cooking assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300,
        temperature=0.7,
    )

    # Display the recipe.
    if response.choices:
        recipe = response.choices[0].message.content
        st.write(recipe)
    else:
        st.write("No recipe could be generated. Please try again.")
