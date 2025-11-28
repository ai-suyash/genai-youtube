TOPIC_EXTRACTION_PROMPT = """
You are an expert research analyst. Your task is to analyze the provided
text and perform a detailed extraction of its key components for a podcast
scriptwriter. Do not invent information. All output must be based strictly
on the provided content.

Analyze the given research paper and identify
- The main topic of the content
- A summary of the content's central argument and conclusion.

Then, extract the 5 most important subtopics. Important guidelines for
subtopic selection:
- Avoid generic topics like 'Introduction', 'Background', or 'Conclusion'.
- Each subtopic should be suitable for an in-depth, discussion.

For each subtopic, extract the following:

1. A descriptive and enticing title.
2. A summary of the subtopic. Maximum of two paragraphs. If relevant, include
   any supporting evidence, specific examples, or data points mentioned in the
   text.
3. Key Statistics & Data. A list of the most impactful statistics, figures, or
   data points mentioned.

Provide your response in a JSON format that can be directly parsed.
"""