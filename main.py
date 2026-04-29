from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class EnglishLearningState(TypedDict):
    original_sentence: str
    corrected_sentence: str
    grammar_feedback: str
    vocabulary_feedback: str
    teacher_feedback: str
    final_answer: str


def grammar_agent(state: EnglishLearningState):
    sentence = state["original_sentence"]
    corrected = sentence.strip()
    feedback_items = []

    # Capitalize first letter
    if corrected and corrected[0].islower():
        corrected = corrected[0].upper() + corrected[1:]
        feedback_items.append("Start the sentence with a capital letter.")

    # Fix lowercase "i"
    if " i " in corrected:
        corrected = corrected.replace(" i ", " I ")
        feedback_items.append('Use "I" instead of "i".')

    # Fix "i'll"
    if "i'll" in corrected.lower():
        corrected = corrected.replace("i'll", "I'll")
        corrected = corrected.replace("I'll", "I'll")
        feedback_items.append('Use "I’ll" with a capital "I".')

    # Fix common phrase: want learn
    if "want learn" in corrected.lower():
        corrected = corrected.replace("want learn", "want to learn")
        corrected = corrected.replace("Want learn", "Want to learn")
        feedback_items.append('Use "want to learn", not "want learn".')

    # Fix common phrase: need learn
    if "need learn" in corrected.lower():
        corrected = corrected.replace("need learn", "need to learn")
        corrected = corrected.replace("Need learn", "Need to learn")
        feedback_items.append('Use "need to learn", not "need learn".')

    # Fix LangGraph capitalization
    if "langgraph" in corrected.lower():
        corrected = corrected.replace("langgraph", "LangGraph")
        corrected = corrected.replace("Langgraph", "LangGraph")
        feedback_items.append('Write the tool name as "LangGraph".')

    # Fix project phrase
    if "from the English Learning Multi-Agent Assistant" in corrected:
        corrected = corrected.replace(
            "from the English Learning Multi-Agent Assistant",
            "with the English Learning Multi-Agent Assistant"
        )
        feedback_items.append('Use "with the project" instead of "from the project".')

    if not feedback_items:
        feedback = "Grammar Agent:\nYour sentence looks good. I did not find a major grammar mistake."
    else:
        feedback = "Grammar Agent:\n" + "\n".join(f"- {item}" for item in feedback_items)

    return {
        "corrected_sentence": corrected,
        "grammar_feedback": feedback
    }


def vocabulary_agent(state: EnglishLearningState):
    sentence = state["corrected_sentence"]

    suggestions = []

    if "start" in sentence.lower():
        suggestions.append('"start" is good. You can also say "begin" or "get started with".')

    if "learn" in sentence.lower():
        suggestions.append('"learn" is good. You can also say "study" or "practice", depending on the meaning.')

    if "project" in sentence.lower():
        suggestions.append('"project" is a good word here because you are building something step by step.')

    if not suggestions:
        feedback = "Vocabulary Agent:\nYour vocabulary is understandable."
    else:
        feedback = "Vocabulary Agent:\n" + "\n".join(f"- {item}" for item in suggestions)

    return {
        "vocabulary_feedback": feedback
    }


def teacher_agent(state: EnglishLearningState):
    original = state["original_sentence"]
    corrected = state["corrected_sentence"]
    grammar = state["grammar_feedback"]
    vocabulary = state["vocabulary_feedback"]

    final_answer = f"""
English Learning Assistant

Your original sentence:
{original}

Corrected sentence:
{corrected}

{grammar}

{vocabulary}

Teacher Agent:
Good job. Your meaning is clear. Keep practicing by writing one sentence every day.
"""

    return {
        "teacher_feedback": "The student received grammar and vocabulary feedback.",
        "final_answer": final_answer
    }


graph_builder = StateGraph(EnglishLearningState)

graph_builder.add_node("grammar_agent", grammar_agent)
graph_builder.add_node("vocabulary_agent", vocabulary_agent)
graph_builder.add_node("teacher_agent", teacher_agent)

graph_builder.add_edge(START, "grammar_agent")
graph_builder.add_edge("grammar_agent", "vocabulary_agent")
graph_builder.add_edge("vocabulary_agent", "teacher_agent")
graph_builder.add_edge("teacher_agent", END)

graph = graph_builder.compile()

while True:
    sentence = input("\nWrite your English sentence, or type 'exit' to quit: ")

    if sentence.lower() == "exit":
        print("Goodbye! Keep practicing English.")
        break

    result = graph.invoke({
        "original_sentence": sentence,
        "corrected_sentence": "",
        "grammar_feedback": "",
        "vocabulary_feedback": "",
        "teacher_feedback": "",
        "final_answer": ""
    })

    print(result["final_answer"])