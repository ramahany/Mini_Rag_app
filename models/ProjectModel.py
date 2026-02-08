from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Project

class ProjectModel(BaseDataModel): 
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    # how to access a async function in _init_ ?? you cant heeheheheh so use a wraper and use it for init the class to do both tasks
    @classmethod
    async def create_instance(cls, db_client:object): # it take the same params the init should be takin 
        #the __init__()
        instance = cls(db_client)
        # call the async function 
        await instance.init_collection()
        #return the instance
        return instance
    

    # u should create the indexing only the first time when u create the collection itself other wise you will have to do that in mongo manually
    async def init_collection(self): 
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections: 
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes: 
                await self.collection.create_index(
                    index["key"],
                    name=index["name"], 
                    unique = index["unique"]
                )

    # Creating a new doc (project) with a field of project_id == id givien by the user
    async def create_project(self, project: Project): 
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        
        return project 
    
    # if you have this project just retrieve it , if not create a new project 
    async def get_project_or_create_one(self, project_id : str): 
        
        record = await self.collection.find_one({
            "project_id" : project_id
        })

        if record is None : 
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            print(project)
            return project
        

        return Project(**record)

    async def get_all_projects(self, page : int = 1, page_size: int = 10): 

        # count total number of documents
        total_documents = await self.collection.count_documents({}) #if you had a fileter you could put it here 

        # calculate number of pages 
        total_pages = total_documents // page_size if total_documents % page_size == 0 else 1 + total_documents // page_size

        # creating a cursor with the documents
        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)

        # data = list(cursor) # possible but will load all data at once

        # load them one at a time 
        projects = []
        for document in cursor :
            projects.append(
                Project(**document)
            )
        
        return projects, total_pages
            


