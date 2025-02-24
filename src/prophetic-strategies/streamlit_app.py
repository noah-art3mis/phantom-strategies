import streamlit as st
from pathlib import Path
from utils import get_data, update_tokens
from costs import get_n_tokens
from constants import STRATEGIES
from Prophet import Prophet

DEBUG = True

if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = 0

st.title("Phantom Strategies")
st.write("")

### PARAMETERS ###

with st.sidebar:
    st.header("Parameters")

    strategy = st.radio(
        label="Strategy",
        options=[x["name"] for x in STRATEGIES],
        captions=[x["description"] for x in STRATEGIES],
    )

    iterations = st.slider("Iterations", 0, 5, 2)

    temperature = st.slider("Temperature", 0.0, 1.0, 1.0)

    ### CONTACT ###

    st.divider()
    st.write("Made by Gustavo Costa")
    st.write(
        "[Source code](https://github.com/noah-art3mis/prophetic-strategies) / [Blog](https://gustavocosta.psc.br/) / [Instagram](https://www.instagram.com/simulacro.psi/) / [Twitter](https://x.com/simulacrum_ai) / [LinkedIn](https://www.linkedin.com/in/gustavoarcos/)"
    )
    st.write("")
    st.write("")

### RATE LIMITING ###

if st.session_state.tokens_used >= 50:
    p1, p2 = st.columns(2)
    progress_bar = p1.progress(
        st.session_state.tokens_used, text="Prophet's lack of patience"
    )

if st.session_state.tokens_used >= 100:
    st.write("The oracle tires of your antics. Please come another time.")
else:

    ### INPUT ###

    with st.form("my_form", border=False):
        st.write("")
        question = st.text_input("What is it that you desire (not) to know?")
        submit = st.form_submit_button("O, Prophet...")

    ### RESULT ###

    if submit:

        prophet = Prophet.get_prophet(
            strategy=strategy,  # type: ignore
            api_key=st.secrets["OPENAI_API_KEY"],
            temp=temperature,
            strategies=[x["name"] for x in STRATEGIES],
        )

        df = get_data(prophet.table)
        search_result = prophet.search(question, df)
        stream = prophet.generate(search_result["content"], message_history=[])

        finished_completion = st.write_stream(stream)

        ### REFERENCE ###

        if type(finished_completion) is str:
            reference = prophet.generate_reference(finished_completion, search_result)

            st.write("")

            reference_author = f"{prophet.author}, the {prophet.name}"
            st.caption(
                f'<div style="text-align: right;">{reference_author}</div>',
                unsafe_allow_html=True,
            )

            reference_book = reference["book"]
            st.caption(
                f'<div style="text-align: right;">{reference_book}</div>',
                unsafe_allow_html=True,
            )

            sentence_number = "Sentence " + str(reference["sentence"])
            st.caption(
                f'<div style="text-align: right;">{sentence_number}</div>',
                unsafe_allow_html=True,
            )

    ### FEEDBACK ###

    # def thanks():
    #     st.toast("The prophet thanks you for the feedback.")

    # if st.session_state.feedback is None:
    #     feedback = st.feedback(on_change=thanks)
