import streamlit as st
import pandas as pd
import openai
import re

def extract_words_with_slashes(lyrics):
    # Use regex to find words enclosed by slashes with possible punctuation
    words_with_slashes = re.findall(r'/(?P<word>[\w\s]+?)[^\w\s]*[^\w\s]', lyrics)
    return words_with_slashes

def fetch_word_info(word, api_key):
    openai.api_key = api_key
    prompt = f"Define the word '{word}', provide a synonym, and an example sentence. The response format should begin with 'Definition:', followed by 'Synonym:' (if available) and 'Example:' after the definition and synonym (if available)."
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=200
    )
    
    if response and 'choices' in response:
        for choice in response['choices']:
            word_info = choice['text'].strip()
            # Adjust this section to handle different response formats
            if word_info.startswith("Definition:"):
                definition = word_info.split("Synonym:")[0].replace("Definition:", "").strip()
                synonym = re.search(r"Synonym:(.*?)(Example:|$)", word_info, re.DOTALL)
                synonym = synonym.group(1).strip() if synonym else "No synonym available"
                example = word_info.split("Example:")[1].strip() if "Example:" in word_info else "No example available"
                return definition, synonym, example
            # Adjust for different response structures or absence of specific formatting
            else:
                return "No definition found for this word.", "No synonym available", "No example available"
    
    return "No definition found for this word.", "No synonym available", "No example available"

def process_lyrics(lyrics, api_key):
    if not isinstance(lyrics, str):
        st.warning("Please enter lyrics as text.")
        return None
    
    words = extract_words_with_slashes(lyrics)
    
    if not words:
        st.warning("Please use slashes /word/ to indicate the words you want to define.")
        return None
    
    word_data = []
    for word in words:
        definition, synonym, example = fetch_word_info(word, api_key)
        # Format the retrieved word in the example sentence as bold
        # example = example.replace(word, f"<b>{word}</b>")
        word_data.append({"Word": word, "Definition": definition, "Synonym": synonym, "Example": example})
    df = pd.DataFrame(word_data, columns=["Word", "Definition", "Synonym", "Example"])
    return df

def generate_story(words_info, api_key):
    retrieved_words = [row['Word'] for index, row in words_info.iterrows()]
    retrieved_words_str = ", ".join(retrieved_words)
    
    prompt = f"In a world filled with {retrieved_words_str}, something extraordinary happened..., you have to use the retrieved words to create the story"
    
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100
    )
    
    if response and 'choices' in response:
        generated_text = response['choices'][0]['text'].strip()
        story = generated_text
    
    return story

    return story


def main():
    st.title("Words in Lyrics (or in anything) 🎶🎄")
    
    st.write("Enter your English lyrics with words to define between slashes /word/.")
    st.write("Our system will provide definitions, synonyms, and example sentences, along with a concise story (limited to 100 tokens) incorporating the retrieved words. 📖💗")
    st.write("Example: define your /English/ /words/ like this")
    
    api_key = st.sidebar.text_input("Enter Your OpenAI API Key", placeholder="Enter API Key here")
    
    lyrics = st.text_area("Enter Lyrics")
    
    # Applying custom CSS for baby pink background inside the main function
    st.markdown(
        """
        <style>
        body {
            background-color: #FFB6C1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Process"):
        if not api_key:
            st.warning("Please enter your OpenAI API key.")
        else:
            result_df = process_lyrics(lyrics, api_key)
            if result_df is not None:
                st.success("Words processed successfully. See results below.")
                st.dataframe(result_df)
                
                # Generate a story using the retrieved words
                generated_story = generate_story(result_df, api_key)  # Pass the API key
                st.info("Short Story incorporating retrieved words:")
                st.info(generated_story)
            else:
                st.warning("No results to display. Please check your input.")
if __name__ == "__main__":
    main()