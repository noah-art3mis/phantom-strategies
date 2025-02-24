STRATEGIES = [
    {
        "name": "Oracular",
        "description": "Semantic search (SS) using `text-embedding-3-small`",
    },
    {
        "name": "Fallacious",
        "description": "SS + `gpt-4o` finetuned on Lacan's _Seminar Book V_",
    },
    {
        "name": "Ficticious",
        "description": "SS + `gpt-4o-mini` (FT) finetuned on Lacan's _Seminar Book V_",
    },
    {
        "name": "Erratic",
        "description": "Mystery sampling",
    },
    {
        "name": "Mercurial",
        "description": "Mystery strategy",
    },
    {
        "name": "Chimerical",
        "description": "SS + FT on Steiner's _An Outline of Occult Science_",
    },
    {
        "name": "Spectral",
        "description": "SS + FT on Hegel's _Philosophy of Mind_",
    },
    {
        "name": "Quixotic",
        "description": "SS + FT on Marcus Aurelius' _Meditations_",
    },
    {
        "name": "Apocryphal",
        "description": "SS + FT on Mill's _On Liberty_",
    },
]


ALLOWED_BASE_MODELS = [
    {
        "model": "gpt-4o-2024-08-06",
        "input_cost": 2.5 / 1_000_000,
        "output_cost": 10.0 / 1_000_000,
    },
    {
        "model": "gpt-4o-mini-2024-07-18",
        "input_cost": 0.15 / 1_000_000,
        "output_cost": 0.60 / 1_000_000,
    },
    {
        "model": "claude-3-haiku-20240307",
        "input_cost": 0.25 / 1_000_000,
        "output_cost": 1.25 / 1_000_000,
    },
    {"model": "llama3", "input_cost": 0.0, "output_cost": 0.0},
    # case minilm
    # case embedding openai
    # case generative local
    # cae reranker
]

REFERENCE_PROMPT = """Come up with an interesting title for a book or article this text might belong to. The title should have a similar style to these examples: 

- On My Antecedents
- Beyond the _Reality Principle_
- The Mirror Stage as Formative of the _I_ Function as Revealed in Psychoanalytic Experience
- Aggressiveness in Psychoanalysis
- A Theoretical Introduction to the Functions of Psychoanalysis in Criminology
- Presentation on Psychical Causality
- Logical Time and the Assertion of Anticipated Certainty
- Presentation on Transference
- On the Subject Who Is Finally in Question
- The Function and Field of Speech and Language in Psychoanalysis
- Variations on the Standard Treatment
- On a Purpose
- Introduction to Jean Hyppolite's Commentary on Freud's _Verneinung_
- Response to Jean Hyppolite's Commentary on Freud's _Verneinung_
- The Freudian Thing, or the Meaning of the Return to Freud in Psychoanalysis
- Psychoanalysis and Its Teaching
- The Situation of Psychoanalysis and the Training of Psychoanalysts in 1956
- The Instance of the Letter in the Unconscious, or Reason Since Freud
- On a Question Prior to Any Possible Treatment of Psychosis
- The Direction of the Treatment and the Principles of Its Power
- Remarks on Daniel Lagache's Presentation: _Psychoanalysis and Personality_
- The Signification of the Phallus
- In Memory of Ernest Jones: On His Theory of Symbolism
- On an Ex Post Facto Syllabary
- Guiding Remarks for a Convention on Female Sexuality
- The Youth of Gide, or the Letter and Desire
- Kant with Sade
- The Subversion of the Subject and the Dialectic of Desire in the Freudian Unconscious
- Position of the Unconscious
- On Freud's _Trieb_ and the Psychoanalyst's Desire
- Science and Truth

This is the text in question:

###

{{SNIPPET}}

###

Respond exclusively with the title and nothing else."""

# ref_claude = """You are tasked with creating an interesting and thought-provoking title for a book or article based on a given text snippet. The title should be in a similar style to the examples provided in the task description.

# Here is the text snippet you will be working with:

# <snippet>
# {{SNIPPET}}
# </snippet>

# Guidelines for creating the title:
# 1. Analyze the main themes, concepts, or ideas present in the text snippet.
# 2. Consider using abstract or philosophical language that captures the essence of the text.
# 3. You may use underscores to emphasize certain words or phrases, as seen in some of the example titles.
# 4. The title can be a phrase, a question, or a statement.
# 5. Aim for a title that is intriguing and provocative, encouraging readers to explore the content further.
# 6. Feel free to use metaphors, allusions, or wordplay if appropriate.

# The title should have a similar style to these examples:

# <title_examples>
# - On My Antecedents
# - Beyond the _Reality Principle_
# - The Mirror Stage as Formative of the _I_ Function as Revealed in Psychoanalytic Experience
# - Aggressiveness in Psychoanalysis
# - A Theoretical Introduction to the Functions of Psychoanalysis in Criminology
# - Presentation on Psychical Causality
# - Logical Time and the Assertion of Anticipated Certainty
# - Presentation on Transference
# - On the Subject Who Is Finally in Question
# - The Function and Field of Speech and Language in Psychoanalysis
# - Variations on the Standard Treatment
# - On a Purpose
# - Introduction to Jean Hyppolite's Commentary on Freud's _Verneinung_
# - Response to Jean Hyppolite's Commentary on Freud's _Verneinung_
# - The Freudian Thing, or the Meaning of the Return to Freud in Psychoanalysis
# - Psychoanalysis and Its Teaching
# - The Situation of Psychoanalysis and the Training of Psychoanalysts in 1956
# - The Instance of the Letter in the Unconscious, or Reason Since Freud
# - On a Question Prior to Any Possible Treatment of Psychosis
# - The Direction of the Treatment and the Principles of Its Power
# - Remarks on Daniel Lagache's Presentation: _Psychoanalysis and Personality_
# - The Signification of the Phallus
# - In Memory of Ernest Jones: On His Theory of Symbolism
# - On an Ex Post Facto Syllabary
# - Guiding Remarks for a Convention on Female Sexuality
# - The Youth of Gide, or the Letter and Desire
# - Kant with Sade
# - The Subversion of the Subject and the Dialectic of Desire in the Freudian Unconscious
# - Position of the Unconscious
# - On Freud's _Trieb_ and the Psychoanalyst's Desire
# - Science and Truth
# </title_examples>

# Once you have formulated a suitable title, provide your response in the following format:

# <title>
# Your created title goes here
# </title>

# Ensure that you only include the title within the tags, with no additional explanation or commentary."""
