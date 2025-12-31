from typing import List, Tuple
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class ResponseEngine:
    """
    Generates grounded answers from ranked document chunks.
    """

    RESPONSE_PROMPT = PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are Libris, a factual knowledge assistant.

Answer the user's question using ONLY the information in the provided context.
You may summarize or explain ideas that are explicitly described in the context.
Do NOT introduce outside knowledge or unsupported claims.
Format your answers in a markdown format that is easy to read.

If the context does not contain enough information to answer the question, respond with:
"I don't have that information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
""".strip()
    )

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_context_chars: int = 1500,
    ):
        """
        Args:
            model_name: OpenAI model to use
            temperature: generation temperature (keep at 0.0 for factual responses)
            max_context_chars: max characters to include per chunk
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_context_chars = max_context_chars

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
        )

    def _format_context(
        self,
        ranked_chunks: List[Tuple[Document, float]],
    ) -> str:
        """
        Formats ranked chunks into a structured context block.
        """
        blocks = []

        for rank, (doc, score) in enumerate(ranked_chunks, start=1):
            meta = doc.metadata
            content = doc.page_content[: self.max_context_chars].replace("\n", " ")

            blocks.append(
                f"""[Chunk {rank}]

Content:
{content}
"""
            )

        return "\n".join(blocks)

    def generate_response(
        self,
        question: str,
        ranked_chunks: List[Tuple[Document, float]],
    ) -> str:
        """
        Generates an answer grounded in retrieved chunks.

        Args:
            question: user query
            ranked_chunks: deduplicated, ranked list of (Document, score)

        Returns:
            Answer string
        """
        if not ranked_chunks:
            return "I don't have that information in the provided documents."

        context = self._format_context(ranked_chunks)

        prompt = self.RESPONSE_PROMPT.format(
            question=question,
            context=context,
        )

        response = self.llm.invoke(prompt)

        return response.content.strip()
