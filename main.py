from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class EnglishLearningState(TypedDict):
    original_sentence: str
    corrected_sentence: str
    grammar_feedback: str
    vocabulary_feedback: str
    teacher_feedback: str
    final_answer: str
    has_mistakes: bool


def grammar_agent(state: EnglishLearningState):
    sentence = state["original_sentence"]
    corrected = sentence.strip()
    feedback_items = []

    if corrected and corrected[0].islower():
        corrected = corrected[0].upper() + corrected[1:]
        feedback_items.append("Start the sentence with a capital letter.")

    if " i " in corrected:
        corrected = corrected.replace(" i ", " I ")
        feedback_items.append('Use "I" instead of "i".')

    if "i'll" in corrected.lower():
        corrected = corrected.replace("i'll", "I'll")
        corrected = corrected.replace("I'll", "I'll")
        feedback_items.append('Use "I’ll" with a capital "I".')

    if "want learn" in corrected.lower():
        corrected = corrected.replace("want learn", "want to learn")
        corrected = corrected.replace("Want learn", "Want to learn")
        feedback_items.append('Use "want to learn", not "want learn".')

    if "need learn" in corrected.lower():
        corrected = corrected.replace("need learn", "need to learn")
        corrected = corrected.replace("Need learn", "Need to learn")
        feedback_items.append('Use "need to learn", not "need learn".')

    if "need practice" in corrected.lower():
        corrected = corrected.replace("need practice", "need to practice")
        corrected = corrected.replace("Need practice", "Need to practice")
        feedback_items.append('Use "need to practice", not "need practice".')

    if "langgraph" in corrected.lower():
        corrected = corrected.replace("langgraph", "LangGraph")
        corrected = corrected.replace("Langgraph", "LangGraph")
        feedback_items.append('Write the tool name as "LangGraph".')

    if "from the English Learning Multi-Agent Assistant" in corrected:
        corrected = corrected.replace(
            "from the English Learning Multi-Agent Assistant",
            "with the English Learning Multi-Agent Assistant"
        )
        feedback_items.append('Use "with the project" instead of "from the project".')

    has_mistakes = len(feedback_items) > 0

    if not has_mistakes:
        feedback = "Grammar Agent:\nYour sentence looks good."
    else:
        feedback = "Grammar Agent:\n" + "\n".join(f"- {item}" for item in feedback_items)

    return {
        "corrected_sentence": corrected,
        "grammar_feedback": feedback,
        "has_mistakes": has_mistakes
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
Good job. Your meaning is clear. Review the corrections and try to write another sentence.
"""

    return {
        "teacher_feedback": "The student received correction feedback.",
        "final_answer": final_answer
    }


def praise_agent(state: EnglishLearningState):
    original = state["original_sentence"]

    final_answer = f"""
English Learning Assistant

Your sentence:
{original}

Praise Agent:
Great job! Your sentence looks good.

Teacher Agent:
Try writing a longer sentence next time so you can practice more English.
"""

    return {
        "teacher_feedback": "The student received praise feedback.",
        "final_answer": final_answer
    }


def route_after_grammar(state: EnglishLearningState):
    if state["has_mistakes"]:
        return "vocabulary_agent"
    else:
        return "praise_agent"


graph_builder = StateGraph(EnglishLearningState)

graph_builder.add_node("grammar_agent", grammar_agent)
graph_builder.add_node("vocabulary_agent", vocabulary_agent)
graph_builder.add_node("teacher_agent", teacher_agent)
graph_builder.add_node("praise_agent", praise_agent)

graph_builder.add_edge(START, "grammar_agent")

graph_builder.add_conditional_edges(
    "grammar_agent",
    route_after_grammar,
    {
        "vocabulary_agent": "vocabulary_agent",
        "praise_agent": "praise_agent"
    }
)

graph_builder.add_edge("vocabulary_agent", "teacher_agent")
graph_builder.add_edge("teacher_agent", END)
graph_builder.add_edge("praise_agent", END)

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
        "final_answer": "",
        "has_mistakes": False
    })

    print(result["final_answer"])