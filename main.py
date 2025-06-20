from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, GetCoreSchemaHandler, model_validator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Placeholder for random icons (you can replace these with actual paths/URLs)
DEFAULT_ICONS = [
    "https://api.iconify.design/material-symbols:lightbulb-outline.svg",
    "https://api.iconify.design/material-symbols:handshake-outline.svg",
    "https://api.iconify.design/material-symbols:settings-outline.svg",
    "https://api.iconify.design/material-symbols:support-agent-outline.svg",
    "https://api.iconify.design/material-symbols:security-outline.svg",
]

# Initialize FastAPI app
app = FastAPI(
    title="Help Center API",
    description="A centralized help and guidance server system for organizational applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.help_center

# Pydantic models
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler) -> JsonSchemaValue:
        return {"type": "string", "examples": ["507f1f77bcf86cd799439011"]}

class Media(BaseModel):
    type: str = Field(..., description="Type of media (image or video)", example="image")
    url: str = Field(..., description="URL of the media", example="https://example.com/image.jpg")
    alt_text: str = Field(..., description="Alternative text for accessibility", example="Screenshot of the dashboard")

class TipBase(BaseModel):
    tip_id: int = Field(..., description="Unique integer ID for the tip", example=2001)
    title: str = Field(..., description="Title of the tip", example="How to create a new project")
    description: str = Field(..., description="Description of the tip", example="To create a new project, click the '+' button in the top right corner...")
    media: Optional[Media] = Field(None, description="Media associated with the tip")
    display_order: int = Field(default=1, description="Order in which the tip should be displayed", example=1)
    topic_id: int = Field(..., description="ID of the parent topic", example=1001)

class TipCreate(TipBase):
    tip_id: Optional[int] = Field(None, description="Unique integer ID for the tip (required for update, optional for creation)", example=2001)
    class Config:
        json_schema_extra = {
            "example": {
                "tip_id": 2001,
                "title": "How to create a new project",
                "description": "To create a new project, click the '+' button in the top right corner...",
                "media": {
                    "type": "image",
                    "url": "https://example.com/image.jpg",
                    "alt_text": "Screenshot of the dashboard"
                },
                "display_order": 1,
                "topic_id": 1001,
                "tip_id": 2001  # Optional for creation, required for update
            }
        }

class Tip(TipBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tip_id": 2001,
                "title": "How to create a new project",
                "description": "To create a new project, click the '+' button in the top right corner...",
                "media": {
                    "type": "image",
                    "url": "https://example.com/image.jpg",
                    "alt_text": "Screenshot of the dashboard"
                },
                "display_order": 1,
                "topic_id": 1001,
                "created_at": "2024-03-15T10:30:00",
                "updated_at": "2024-03-15T10:30:00"
            }
        }

class TopicBase(BaseModel):
    title: str = Field(..., description="Title of the topic", example="Project Management")
    description: Optional[str] = Field(None, description="Description of the topic", example="Tips and tricks for managing projects effectively")
    display_order: int = Field(default=1, description="Order in which the topic should be displayed", example=1)
    isNew: bool = Field(default=True, description="Indicates if the topic is new", example=True)
    icon: str = Field(default="", description="URL of the topic icon", example="https://example.com/icon.svg")

class TopicCreate(TopicBase):
    topic_id: Optional[int] = Field(None, description="Unique integer ID for the topic (optional for creation, required for update)", example=1001)

    @model_validator(mode='before')
    @classmethod
    def set_random_icon_if_none(cls, values):
        if not values.get('icon'):
            values['icon'] = random.choice(DEFAULT_ICONS)
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Management",
                "description": "Tips and tricks for managing projects effectively",
                "display_order": 1,
                "isNew": True,
                "icon": ""
            }
        }

class Topic(TopicBase):
    topic_id: int = Field(..., description="Unique integer ID for the topic", example=1001)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tipCount: int = Field(default=0, description="Number of tips in this topic", example=5)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "topic_id": 1001,
                "title": "Project Management",
                "description": "Tips and tricks for managing projects effectively",
                "created_at": "2024-03-15T10:30:00",
                "updated_at": "2024-03-15T10:30:00",
                "tipCount": 1
            }
        }

class SearchResult(BaseModel):
    type: str = Field(..., description="Type of result (topic or tip)", example="tip")
    id: str = Field(..., description="ID of the result", example="507f1f77bcf86cd799439011")
    title: str = Field(..., description="Title of the result", example="How to create a new project")
    description: str = Field(..., description="Description of the result", example="To create a new project...")
    topic_id: Optional[str] = Field(None, description="ID of the parent topic (for tips only)", example="507f1f77bcf86cd799439012")
    topic_title: Optional[str] = Field(None, description="Title of the parent topic (for tips only)", example="Project Management")
    relevance_score: float = Field(..., description="Search relevance score", example=0.95)

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int
    query: str
    limit: int
    offset: int

# API Routes
@app.post("/api/topics", response_model=Topic, status_code=201, tags=["Topics"])
async def create_or_update_topic(topic: TopicCreate):
    """
    Create a new topic or update an existing one.
    If topic_id is provided and exists, the topic will be updated.
    If topic_id is not provided or doesn't exist, a new topic will be created.
    
    - **topic_id**: Unique integer ID for the topic (optional for creation, required for update)
    - **title**: Title of the topic
    - **description**: Optional description of the topic
    """
    topic_dict = topic.model_dump()
    if topic.topic_id:
        # Check if topic_id exists for update
        existing = await db.topics.find_one({"topic_id": topic.topic_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        original_display_order = existing.get("display_order")
        new_display_order = topic_dict.get("display_order")

        if new_display_order is not None and new_display_order != original_display_order:
            # Adjust display_order of other topics
            if new_display_order > original_display_order:
                # Moving to a higher display_order (down the list)
                await db.topics.update_many(
                    {
                        "topic_id": {"$ne": topic.topic_id},
                        "display_order": {"$gt": original_display_order, "$lte": new_display_order}
                    },
                    {"$inc": {"display_order": -1}}
                )
            elif new_display_order < original_display_order:
                # Moving to a lower display_order (up the list)
                await db.topics.update_many(
                    {
                        "topic_id": {"$ne": topic.topic_id},
                        "display_order": {"$gte": new_display_order, "$lt": original_display_order}
                    },
                    {"$inc": {"display_order": 1}}
                )

        # Update existing topic
        topic_dict["updated_at"] = datetime.utcnow()
        await db.topics.update_one(
            {"topic_id": topic.topic_id},
            {"$set": topic_dict}
        )
        updated_topic = await db.topics.find_one({"topic_id": topic.topic_id})
        # Calculate tipCount for the updated topic
        tip_count = await db.tips.count_documents({"topic_id": updated_topic["topic_id"]})
        updated_topic["tipCount"] = tip_count
        return Topic(**updated_topic)
    else:
        # Create new topic with app-generated topic_id
        # Find the maximum topic_id to assign the next available one
        max_topic = await db.topics.find_one(
            {}, sort=[("topic_id", -1)]
        )
        next_topic_id = (max_topic["topic_id"] + 1) if max_topic else 1 # Start from 1 if no topics exist
        
        topic_dict["topic_id"] = next_topic_id
        topic_dict["created_at"] = datetime.utcnow()
        topic_dict["updated_at"] = datetime.utcnow()
        
        # Handle display_order for new topics
        if "display_order" in topic_dict and topic_dict["display_order"] is not None:
            # User explicitly provided a display_order, shift existing topics
            await db.topics.update_many(
                {"display_order": {"$gte": topic_dict["display_order"]}},
                {"$inc": {"display_order": 1}}
            )
        else:
            # Assign display_order as the count of existing topics if not provided by user
            topic_count = await db.topics.count_documents({})
            topic_dict["display_order"] = topic_count

        # Debugging: Print topic_dict before insertion to check icon value
        print(f"Topic dict before insertion: {topic_dict}")

        await db.topics.insert_one(topic_dict)
        created_topic = await db.topics.find_one({"topic_id": next_topic_id})
        # Initialize tipCount for the new topic
        created_topic["tipCount"] = 0
        return Topic(**created_topic)

@app.get("/api/topics", response_model=List[Topic], tags=["Topics"])
async def get_topics():
    topics_cursor = db.topics.find().sort("display_order", 1)
    topics_list = []
    async for t in topics_cursor:
        tip_count = await db.tips.count_documents({"topic_id": t["topic_id"]})
        t["tipCount"] = tip_count
        topics_list.append(Topic(**t))
    return topics_list

@app.get("/api/topics/{topic_id}", response_model=Topic, tags=["Topics"])
async def get_topic(topic_id: int = Path(..., description="The topic_id of the topic to retrieve")):
    topic = await db.topics.find_one({"topic_id": topic_id})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Calculate tipCount for the retrieved topic
    tip_count = await db.tips.count_documents({"topic_id": topic["topic_id"]})
    topic["tipCount"] = tip_count
    
    return Topic(**topic)

@app.delete("/api/topics/{topic_id}", status_code=204, tags=["Topics"])
async def delete_topic(topic_id: int = Path(..., description="The topic_id of the topic to delete")):
    result = await db.topics.delete_one({"topic_id": topic_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    await db.tips.delete_many({"topic_id": topic_id})

@app.post("/api/tips", response_model=Tip, status_code=201, tags=["Tips"])
async def create_or_update_tip(tip: TipCreate):
    """
    Create a new tip or update an existing one.
    If tip_id is provided, the tip will be updated.
    If tip_id is not provided, a new tip will be created.
    
    - **topic_id**: The topic_id this tip belongs to
    - **tip_id**: Unique integer ID for the tip (optional for creation, required for update)
    - **title**: Title of the tip
    - **description**: Detailed description of the tip
    - **media**: Optional media associated with the tip
    - **display_order**: Order in which the tip should be displayed
    """
    # Verify topic exists
    topic = await db.topics.find_one({"topic_id": tip.topic_id})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    tip_dict = tip.model_dump()
    
    if tip.tip_id is not None:
        # Update existing tip
        existing = await db.tips.find_one({"tip_id": tip.tip_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        original_display_order = existing.get("display_order")
        new_display_order = tip_dict.get("display_order")

        if new_display_order is not None and new_display_order != original_display_order:
            # Adjust display_order of other tips within the same topic
            if new_display_order > original_display_order:
                # Moving to a higher display_order (down the list)
                await db.tips.update_many(
                    {
                        "topic_id": tip.topic_id,
                        "tip_id": {"$ne": tip.tip_id},
                        "display_order": {"$gt": original_display_order, "$lte": new_display_order}
                    },
                    {"$inc": {"display_order": -1}}
                )
            elif new_display_order < original_display_order:
                # Moving to a lower display_order (up the list)
                await db.tips.update_many(
                    {
                        "topic_id": tip.topic_id,
                        "tip_id": {"$ne": tip.tip_id},
                        "display_order": {"$gte": new_display_order, "$lt": original_display_order}
                    },
                    {"$inc": {"display_order": 1}}
                )

        tip_dict["updated_at"] = datetime.utcnow()
        await db.tips.update_one(
            {"tip_id": tip.tip_id},
            {"$set": tip_dict}
        )
        updated_tip = await db.tips.find_one({"tip_id": tip.tip_id})
        return Tip(**updated_tip)
    else:
        # Create new tip
        # Generate a new tip_id (you might want to implement a more sophisticated ID generation)
        last_tip = await db.tips.find_one(sort=[("tip_id", -1)])
        new_tip_id = (last_tip["tip_id"] + 1) if last_tip else 2001
        
        tip_dict["tip_id"] = new_tip_id
        tip_dict["created_at"] = datetime.utcnow()
        tip_dict["updated_at"] = datetime.utcnow()
        
        # Handle display_order for new tips
        if "display_order" in tip_dict and tip_dict["display_order"] is not None:
            # User explicitly provided a display_order, shift existing tips in this topic
            await db.tips.update_many(
                {
                    "topic_id": tip.topic_id,
                    "display_order": {"$gte": tip_dict["display_order"]}
                },
                {"$inc": {"display_order": 1}}
            )
        else:
            # Assign display_order as the count of existing tips in this topic if not provided by user
            tip_count = await db.tips.count_documents({"topic_id": tip.topic_id})
            tip_dict["display_order"] = tip_count

        await db.tips.insert_one(tip_dict)
        created_tip = await db.tips.find_one({"tip_id": new_tip_id})
        return Tip(**created_tip)

@app.get("/api/topics/{topic_id}/tips", response_model=List[Tip], tags=["Tips"])
async def get_tips_by_topic(topic_id: int = Path(..., description="The topic_id to get tips for")):
    tips = await db.tips.find({"topic_id": topic_id}).sort("display_order", 1).to_list(length=None)
    return [Tip(**t) for t in tips]

@app.get("/api/tips/{tip_id}", response_model=Tip, tags=["Tips"])
async def get_tip(tip_id: int = Path(..., description="The tip_id of the tip to retrieve")):
    tip = await db.tips.find_one({"tip_id": tip_id})
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    return Tip(**tip)

@app.delete("/api/tips/{tip_id}", status_code=204, tags=["Tips"])
async def delete_tip(tip_id: int = Path(..., description="The tip_id of the tip to delete")):
    result = await db.tips.delete_one({"tip_id": tip_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tip not found")

@app.get("/api/tips", response_model=List[Tip], tags=["Tips"])
async def get_all_tips():
    """
    Retrieve a list of all tips, sorted by display_order.
    """
    tips = await db.tips.find().sort("display_order", 1).to_list(length=None)
    return [Tip(**t) for t in tips]

@app.get("/api/search", response_model=SearchResponse, tags=["Search"])
async def search(
    q: str = Query(..., description="Search query string"),
    limit: int = Query(20, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Search across topics and tips with partial matching.
    
    - **q**: Search query string
    - **limit**: Maximum number of results to return (default: 20)
    - **offset**: Number of results to skip (default: 0)
    """
    # Use regex for partial matching
    search_query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
    }
    
    # Search in topics
    topic_results = await db.topics.find(
        search_query
    ).skip(offset).limit(limit).to_list(length=None)
    
    # Search in tips
    tip_results = await db.tips.find(
        search_query
    ).skip(offset).limit(limit).to_list(length=None)
    
    # Combine and format results
    results = []
    
    for topic in topic_results:
        # Calculate a simple relevance score based on match position
        title_match = topic["title"].lower().find(q.lower())
        desc_match = topic.get("description", "").lower().find(q.lower())
        relevance = 1.0
        if title_match == 0:  # Match at start of title
            relevance = 1.0
        elif title_match > 0:  # Match in title
            relevance = 0.8
        elif desc_match >= 0:  # Match iFn description
            relevance = 0.6
            
        results.append(SearchResult(
            type="topic",
            id=str(topic["_id"]),
            title=topic["title"],
            description=topic.get("description", ""),
            relevance_score=relevance
        ))
    
    for tip in tip_results:
        topic = await db.topics.find_one({"_id": tip["topic_id"]})
        # Calculate a simple relevance score based on match position
        title_match = tip["title"].lower().find(q.lower())
        desc_match = tip["description"].lower().find(q.lower())
        relevance = 1.0
        if title_match == 0:  # Match at start of title
            relevance = 1.0
        elif title_match > 0:  # Match in title
            relevance = 0.8
        elif desc_match >= 0:  # Match iFn description
            relevance = 0.6
            
        results.append(SearchResult(
            type="tip",
            id=str(tip["_id"]),
            title=tip["title"],
            description=tip["description"],
            topic_id=str(tip["topic_id"]),
            topic_title=topic["title"] if topic else None,
            relevance_score=relevance
        ))
    
    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Get total count
    total_count = len(results)
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        query=q,
        limit=limit,
        offset=offset
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 