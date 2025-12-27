import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task






@CrewBase
class EthicalAiCommitMessageGeneratorWithGovernanceCrew:
    """EthicalAiCommitMessageGeneratorWithGovernance crew"""

    
    @agent
    def generatoragent(self) -> Agent:
        
        return Agent(
            config=self.agents_config["generatoragent"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.0-flash-exp",
                temperature=0.1,
            ),

        )

    @agent
    def validatoragent(self) -> Agent:

        return Agent(
            config=self.agents_config["validatoragent"],


            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,

            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.0-flash-exp",
                temperature=0.1,
            ),

        )
    
    @agent
    def refineragent(self) -> Agent:

        return Agent(
            config=self.agents_config["refineragent"],


            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,

            max_execution_time=None,
            llm=LLM(
                model="gemini/gemini-2.0-flash-exp",
                temperature=0.1,
            ),

        )
    

    
    @task
    def generate_initial_commit_message(self) -> Task:
        return Task(
            config=self.tasks_config["generate_initial_commit_message"],
            markdown=False,
            
            
        )
    
    @task
    def validate_quality_and_safety(self) -> Task:
        return Task(
            config=self.tasks_config["validate_quality_and_safety"],
            markdown=False,
            
            
        )
    
    @task
    def refine_message_with_governance(self) -> Task:
        return Task(
            config=self.tasks_config["refine_message_with_governance"],
            markdown=False,
            
            
        )
    
    @task
    def final_governance_output(self) -> Task:
        return Task(
            config=self.tasks_config["final_governance_output"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the EthicalAiCommitMessageGeneratorWithGovernance crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="gemini/gemini-2.0-flash-exp", temperature=0.1),
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
