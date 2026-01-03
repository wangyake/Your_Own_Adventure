import uuid 
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db, sessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator

router = APIRouter(
    prefix = "/stories",
    tags = ["stories"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)):
    if session_id is None:
        session_id = str(uuid.uuid4())
    return session_id

@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks, # once the job is done, BackgroundTasks goes to LLM to generate a story
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    # httponly:禁止JS脚本通过document.cookie 读取或修改。仅由浏览器在HTTP请求时自动携带到客户端。有效防范XSS攻击窃取session id。
    response.set_cookie(key = "session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id = job_id,
        session_id = session_id,
        theme = request.theme,
        status = "pending"
    )  
    db.add(job)
    db.commit()

    # TODO
    background_tasks.add_task(
        generate_story_task,
        job_id = job_id,
        theme = request.theme,
        session_id = session_id
    )

    return job

def generate_story_task(job_id: str, theme: str, session_id: str):
    db = sessionLocal()
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return 
        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id # todo: update story id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()
        except Exception as e:
            print(e)
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
    finally:
        db.close()


@router.get("/{story_id}/complete", response_model = CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    complete_story = build_complete_story_tree(db, story)
    return complete_story


def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id = node.id,
            content = node.content,
            is_ending = node.is_ending,
            is_winning_ending = node.is_winning_ending,
            options = node.options
        )
        node_dict[node.id] = node_response
    
    root_node = next((node for node in nodes if node.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail = "Story root node not found")
    
    return CompleteStoryResponse(
        id = story.id,
        title = story.title,
        session_id = story.session_id,
        created_at = story.create_at,
        root_node = node_dict[root_node.id],
        all_nodes = node_dict
    )


