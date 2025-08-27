from pydantic import BaseModel

class AuthCredentials(BaseModel):
    username: str
    password: str

class MasterConcept(BaseModel):
    concept: str

class ExerciseRequest(BaseModel):
    concept: str

class SolutionSubmission(BaseModel):
    concept: str
    exercise: str
    solution: str