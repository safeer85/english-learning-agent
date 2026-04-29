from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class EnglishLearningState(TypedDict):
    original_sentence: str
    grammar_feedback: str
    vocabulary_feedback: str
    teacher_feedback: str
    final_answer: str


def grammar_agent(state: EnglishLearningState):
    sentence = state["original_sentence"]

    feedback = f"""
Grammar Agent:
Original sentence: {sentence}

Correction:
- Capitalize "I".
- Use "I'll" instead of "i'll".
- The sentence should start with a capital letter.
"""

    return {
        "grammar_feedback": feedback
    }


def vocabulary_agent(state: EnglishLearningState):
    feedback = """
Vocabulary Agent:
The phrase "start the project" is good.

More natural options:
- "begin the project"
- "start working on the project"
- "get started with the project"
"""

    return {
        "vocabulary_feedback": feedback
    }


def teacher_agent(state: EnglishLearningState):
    original = state["original_sentence"]
    grammar = state["grammar_feedback"]
    vocabulary = state["vocabulary_feedback"]

    final_answer = f"""
English Learning Assistant

Your original sentence:
{original}

Correct sentence:
Okay, I'll start the project with the English Learning Multi-Agent Assistant.

{grammar}

{vocabulary}

Teacher Agent:
Good job. Your meaning is clear. The main things to fix are:
1. Capitalize "Okay".
2. Capitalize "I".
3. Use "I'll" correctly.
4. Keep "English Learning Multi-Agent Assistant" capitalized because it is the project name.
"""

    return {
        "teacher_feedback": "The student understood the project idea.",
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


result = graph.invoke({
    "original_sentence": "okay i'll start the project from the English Learning Multi-Agent Assistant",
    "grammar_feedback": "",
    "vocabulary_feedback": "",
    "teacher_feedback": "",
    "final_answer": ""
})

print(result["final_answer"])