from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

# Create the FastAPI app instance
app = FastAPI()

# Create the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Define the Pydantic model for the User
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    is_admin: bool

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define a dependency with the annotation
db_dependency = Annotated[Session, Depends(get_db)]

# Endpoint to get all users
@app.get("/")
async def get_all(db: db_dependency):
    result = db.query(models.User).all()
    return result

# Endpoint to delete a user by user_id
@app.delete("/deleteUser/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    # Retrieve the user from the database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Check if the user exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Return a response confirming the deletion
    return {"message": "User deleted successfully", "deleted_user": user}
    
# Endpoint to add a new user
@app.post("/addUser/")
async def create_user(user: User, db: db_dependency):
    # Create a new user object from the provided data
    db_addUser = models.User(first_name=user.first_name, last_name=user.last_name, is_admin=user.is_admin)
    
    # Add the user to the database session
    db.add(db_addUser)
    
    # Commit the transaction to save the user to the database
    db.commit()
    
    # Refresh the user object to get its updated state from the database
    db.refresh(db_addUser)

# Endpoint to update user information
@app.put("/updateUser/{user_id}")
async def update_user(user_id: int, updated_user: User, db: db_dependency):
    # Retrieve the user from the database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Check if the user exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user information with the provided data
    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    user.is_admin = updated_user.is_admin
    
    # Commit the changes to the database
    db.commit()
    
    # Return a response confirming the update along with the updated user details
    return {"message": "User updated successfully", "updated_user": updated_user}
