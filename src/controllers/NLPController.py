import logging

from .BaseController import BaseController
# here iam trynig to control vectors db like reset and get info
# i know that i made this frunctions in the provider but lets see why we call it again here
from models.db_schemes import project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
import json 
from fastapi import Request
from typing import List, Dict, Any
import ast
import re
import textwrap

logger = logging.getLogger(__name__)

class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client,template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        self.skills = None
        self.test = None
    def create_collection_name(self, project_id):
        return f"collection_{project_id}"
    
    def reset_vector_db_collection(self,project=project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self,project=project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(#to convert string to dict
            json.dumps(collection_info , default =lambda x: x.__dict__)
        )

    def index_into_vector_db(self,project:project,chunks:list[DataChunk],chunks_ids:list[int],do_reset:bool = False):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [c.chunk_text for c in chunks]
        metadata =[c.chunk_metadata for c in chunks]
        vectors=[self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnum.DOCUMENT.value) for text in texts] # object from LLMProviderFactory which mean object from CohereProvider which contain embed_text
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,)


        _ = self.vectordb_client.insert_many(
            collection_name = collection_name,
            texts = texts,
            metadata=metadata,
            vector = vectors,
            record_ids=chunks_ids,
        )

        return True
    def search_vector_db_collection(self,project:project,text:str,limit:int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vector=self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnum.QUERY.value)
        if not vector or len(vector)==0:
            return False 
        result = self.vectordb_client.search_by_vector(# result is similar to collection info as it contain many diff objects but after apply schema it became a document or dict
            collection_name = collection_name,
            vector = vector,
            limit=limit,
        )

        if not result:
            return False

        return result
    def answer_rag_question(self,project:project,query:str,asset_record,limit:int = 10):
        pormpt=""
        if query == "extract":
            pormpt=f"""
                    You are a professional, domain-agnostic resume parsing system.

                    Rules:
                    - Extract only information explicitly present in the resume.
                    - Do NOT hallucinate.
                    - Use null or empty lists if data is missing.
                    - Return VALID JSON ONLY.
                    - The response must start with {{ and end with }}.
                    - Each skill must be a single, standalone string.
                    - Extract languages and proficiency levels if explicitly mentioned.
                    - Do NOT infer language proficiency.
                    - No explanations.
                    - No markdown.

                    Resume:
                    <<<
                    {asset_record}
                    >>>

                    Return exactly this JSON schema:

                    {{
                    "name": string | null,

                    "skills": [
                        string
                    ],

                    "experience": [
                        {{
                        "role": string,
                        "company": string | null,
                        "type": "Internship" | "Full-time" | "Part-time",
                        "summary": string
                        }}
                    ],

                    "languages": [
                        {{
                        "language": string,
                        "level": string
                        }}
                    ]
                    }}
                    """
        
        answer , full_prompt , chat_history = None , None , None

        """retrieved_documents = self.search_vector_db_collection(project=project,text=query,limit = limit)
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer , full_prompt , chat_history"""
        
        system_prompt = self.template_parser.get("rag","system_prompt")

        
        
        """document_prompt = []
        for i,doc in enumerate(retrieved_documents):
        document_prompt.append(self.template_parser.get("rag","document_prompt",{
            "doc_num" : i+1 ,
            "chunk_text" : doc.text,
            }))"""

        """documents_prompts="\n".join ([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunck_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_documents)
        ])"""

        footer_prompt = self.template_parser.get("rag","footer_prompt", {
                    "query":pormpt,
                   
            })
        
        chat_history = [self.generation_client.construct_prompt(
            prompt = system_prompt,
            role = self.generation_client.enums.SYSTEM.value # instate fo writing coher or open ai enum and i don't know which one is used 
            )]

        full_prompt = "\n\n".join([footer_prompt])

        answer = self.generation_client.generate_text(
            prompt = footer_prompt,# footer_prompt it was full_prompt
            chat_history = chat_history
        )
        s1=""
        s1=answer
        s1=json.loads(s1)
        self.skills = s1['skills']
        self.test = "asd"
        return answer , full_prompt , chat_history
    def skill_gap_system(self,request:Request,query:str,user_skill,role:str):
        answer , full_prompt , chat_history = None , None , None
        prompt_1 = f""" 

                        List only the required skills for the role: {role}.
                        Do not include any descriptions, examples, or extra text.
                        Return the result strictly as a Python list of strings.
                        - only return the names of skills in list no any description just the name
                        Rules:
                        - Each skill must be a single, standalone string.
                        - No explanations.
                        - No markdown.
                        """
        
        response_requierd_skills = self._call_llm_for_json(prompt_1)

        clean_skills = self.split_commas(self.extract_skills(user_skill))
        cleaned = response_requierd_skills
        start = cleaned.find('[')
        end = cleaned.rfind(']')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end+1]
        cleaned_skills_list = ast.literal_eval(cleaned)
        skills_list = self.split_commas(self.extract_skills(cleaned_skills_list))
        gap = set(skills_list) - set(clean_skills)
        full_prompt = prompt_1
        return gap , clean_skills , cleaned_skills_list , skills_list
    
    def split_commas(self,skills):
        result = []
        for skill in skills:
            if "," in skill:
                result.extend([s.strip() for s in skill.split(",")])
            else:
                result.append(skill)
        return result

    def extract_skills(self,skill_list):
        result = []

        for skill in skill_list:

            # استخراج النص داخل الأقواس
            match = re.search(r"\((.*?)\)", skill)

            if match:
                inside = match.group(1)
                subskills = [s.strip() for s in inside.split(",")]

                # إضافة المهارة الأساسية
                main_skill = skill.split("(")[0].strip()
                result.append(main_skill)

                # إضافة المهارات الفرعية
                result.extend(subskills)

            else:
                # إذا لم توجد أقواس
                result.append(skill)

        return result
    

    
    def learning_recommendtion(self,request:Request,user_gap_skill,role:str):
        prompt_3 = textwrap.dedent(f"""
        You are a Skill Gap Learning Advisor.

        I will give you:
        1. A job role.
        2. A list of missing skills that the candidate does NOT have.

        Your task:
        - For EACH missing skill, recommend:
        a) 2 relevant Coursera courses (course title ONLY)
        b) 2 relevant Udemy courses (course title ONLY)
        c) 2 real GitHub project repositories the candidate can build or study

        Important rules:
        - DO NOT add descriptions.
        - DO NOT add explanations.
        - DO NOT include non-skill topics.
        - Return everything as a Python dictionary in this exact format:

        {{
        "skill_name": {{
            "coursera": ["course1", "course2"],
            "udemy": ["course1", "course2"],
            "github_projects": ["repo1", "repo2"]
        }},
        "skill_name_2": {{
            ...
        }}
        }}

        Here are the inputs:
        Role: {role}
        Missing Skills: {user_gap_skill}
        """)

        response_learning_recommendtion = self._call_llm_for_json(prompt_3)
        try:
            return self.parse_llm_json(response_learning_recommendtion)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse learning recommendations: {e}")
            return {}

    def ats_score(self,asset_record,jd_text=None):
        prompt =f"""
        You are an advanced ATS resume analysis engine.

        Tasks:
        1. Infer the professional domain of the resume.
        2. Extract and categorize keywords into:
        - Hard Skills
        - Soft Skills
        - Tools & Platforms
        - Domain-Specific Terms
        3. Count keyword frequency.
        4. Identify missing common keywords for the detected domain.
        5. Analyze readability and content quality.
        6. Detect red flags and weaknesses.
        7. Provide prioritized improvement recommendations.
        8. Compute an Overall ATS Score (0-100).
        """

        if jd_text != None:
            prompt += """
        9. Analyze compatibility between the resume and the provided Job Description.
        10. Compute a CV–JD Match Score (0-100).
        11. Identify matched skills and missing job-required skills.
        """

        prompt += """
        Return ONLY one strictly valid JSON object.
        No explanations, no markdown, no code fences.

        JSON Schema:

        {
        "overall_ats_score": 0,
        "detected_domain": "string",
        "keywords_analysis": {
            "hard_skills": {},
            "soft_skills": {},
            "tools_and_platforms": {},
            "domain_terms": {}
        },
        "missing_common_keywords": [],
        "readability_and_content_quality": {
            "avg_sentence_length": 0,
            "reading_grade_level": 0,
            "skill_density_percent": 0,
            "quantification_percent": 0
        },
        "overused_buzzwords": [],
        "weak_action_phrases": [],
        "red_flags": [],
        """

        if jd_text:
            prompt += """
        "job_match_analysis": {
            "cv_jd_match_score": 0,
            "matched_skills": [],
            "missing_job_skills": []
        },
        """

        prompt += """
        "priority_recommendations": [
            {
            "priority": 1,
            "title": "string",
            "reason": "string",
            "actions": ["string"]
            }
        ]
        }

        Resume Text:
        """ + asset_record

        if jd_text:
            prompt += """

        Job Description Text:
        """ + jd_text

        ats_response = self._call_llm_for_json(prompt)
        ats_response=self.parse_llm_json(ats_response)

        return ats_response["overall_ats_score"] , ats_response["priority_recommendations"]


    '''def parse_llm_json(self,response):
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found in model output")
        return json.loads(json_match.group())'''
    def parse_llm_json(self,response: str) -> Any:
        # remove markdown
        response = response.replace("```json", "").replace("```", "").strip()

        # try direct parse first
        try:
            return json.loads(response)
        except Exception:
            pass

        # fallback: extract outermost JSON object using balanced braces
        start = response.find('{')
        if start != -1:
            depth = 0
            for i in range(start, len(response)):
                if response[i] == '{':
                    depth += 1
                elif response[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(response[start:i+1])
                        except Exception:
                            break

        # fallback: try extracting a JSON array
        start = response.find('[')
        if start != -1:
            depth = 0
            for i in range(start, len(response)):
                if response[i] == '[':
                    depth += 1
                elif response[i] == ']':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(response[start:i+1])
                        except Exception:
                            break

        raise ValueError("No valid JSON found in model output")

    def _call_llm_for_json(self, prompt: str) -> str:
        """A helper method to call the LLM and expect a JSON-like response."""
        system_prompt = "You are a helpful assistant that generates structured data, such as JSON or Python lists."
        chat_history = [self.generation_client.construct_prompt(prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value)]
        footer_prompt = self.template_parser.get("rag", "footer_prompt", {"query": prompt})

        return self.generation_client.generate_text(
            prompt=footer_prompt,
            chat_history=chat_history
        )

    def generate_interview_questions(self, context: str) -> List[str]:
        """Generates dynamic interview questions using an LLM."""
        prompt = textwrap.dedent(f"""
            You are an expert hiring manager. Your task is to generate a list of 7 diverse interview questions based on the provided context.

            Context: "{context}"

            First, analyze the context to determine if it specifies a job role (e.g., "Backend Engineer", "Data Scientist").
            - If a specific role is identified, generate role-specific questions.
            - If the context is generic or a role cannot be determined, generate general behavioral and problem-solving questions suitable for any professional interview.

            The questions should cover:
            - Behavioral questions
            - Technical questions (if a role is identified)
            - Problem-solving or scenario-based questions

            Rules:
            - The difficulty should gradually increase.
            - Return ONLY a valid JSON list of strings.
            - Do not include numbering or introductory text.

            Example format:
            [
                "Question 1",
                "Question 2",
                ...
            ]
        """)

        response = self._call_llm_for_json(prompt)

        try:
            questions = self.parse_llm_json(response)
            if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                return questions
            raise ValueError("LLM did not return a valid list of strings.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse interview questions from LLM: {e}")
            # Fallback to generic questions
            return [
                "Can you tell me about a challenging project you've worked on?",
                "How do you handle tight deadlines and pressure?",
                "What are your greatest strengths and weaknesses?",
                "Describe a time you had a conflict with a team member and how you resolved it.",
                "Where do you see yourself in five years?"
            ]

    def evaluate_interview(self, questions: List[str], answers: List[str]) -> Dict:
        """Evaluates an interview Q&A using an LLM and provides a structured score."""
        
        interview_transcript = "\n\n".join([f"Question: {q}\nAnswer: {a}" for q, a in zip(questions, answers)])

        prompt = textwrap.dedent(f"""
            You are an expert technical recruiter and hiring manager.
            Analyze the following interview transcript and provide a structured evaluation.

            Transcript:
            ---
            {interview_transcript}
            ---

            Evaluation Criteria:
            - Technical Knowledge: Accuracy and depth of technical answers.
            - Problem Solving: Ability to break down problems and propose solutions.
            - Communication: Clarity, conciseness, and professionalism.
            - Relevance: How relevant the answers are to the questions.

            Tasks:
            1.  Provide a score from 1.0 to 10.0 for each of the four criteria.
            2.  Calculate an `overall_score` (the average of the four scores).
            3.  Identify 2-3 key `strengths`.
            4.  Identify 1-2 key `weaknesses` or areas for improvement.
            5.  Write a concise `feedback` summary (2-3 sentences).
            6.  Make a final `decision` from one of these options: "Strong Hire", "Hire", "Hold", "Reject".

            Return ONLY a single, strictly valid JSON object with the following schema. Do not add explanations.

            {{
                "scores": {{
                    "technical_knowledge": float,
                    "problem_solving": float,
                    "communication": float,
                    "relevance": float
                }},
                "overall_score": float,
                "strengths": ["string"],
                "weaknesses": ["string"],
                "feedback": "string",
                "decision": "string"
            }}
        """)

        response = self._call_llm_for_json(prompt)

        try:
            evaluation = self.parse_llm_json(response)
            # Basic validation
            if "overall_score" in evaluation and "decision" in evaluation:
                return evaluation
            raise ValueError("LLM response is missing required evaluation fields.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse interview evaluation from LLM: {e}")
            return {
                "scores": {}, "overall_score": 0.0, "strengths": [], "weaknesses": [],
                "feedback": "Failed to evaluate interview due to an internal error.", "decision": "Reject"
            }

    def parse_interview_email(self, email_body: str, email_subject: str) -> Dict:
        """Extracts structured interview details from an email using an LLM."""
        from datetime import datetime
        prompt = textwrap.dedent(f"""
            You are an expert email parsing system. From the email content below, extract the following details.
            The current UTC time is {datetime.utcnow().isoformat()}.

            - candidate_name: The name of the candidate.
            - interview_datetime: The full date and time of the interview in UTC ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SS).
            - meeting_platform: The name of the video conference platform (e.g., "Google Meet", "Zoom", "Microsoft Teams").
            - meeting_link: The full URL of the meeting link (e.g., a Zoom or Google Meet URL). Extract any URL that looks like a video conference link.
            - job_title: The job title for the interview.

            Email Subject: {email_subject}
            Email Body:
            ---
            {email_body}
            ---

            Return ONLY a single, strictly valid JSON object. Use null for missing fields.
            {{
                "candidate_name": "string | null",
                "interview_datetime": "string | null",
                "meeting_platform": "string | null",
                "meeting_link": "string | null",
                "job_title": "string | null"
            }}
        """)

        response = self._call_llm_for_json(prompt)
        try:
            return self.parse_llm_json(response)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse interview email details from LLM: {e}")
            return {}