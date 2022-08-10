from ast import Try
from sqlite3 import IntegrityError
from typing import List, Optional, Any 
from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioSchemaArtigos, UsuarioSchemaBase, UsuarioSchemaCreate, UsuarioSchemaUp
from core.deps import get_session, get_current_user
from core.security import gerar_hash_senha
from core.auth import autenticar, criar_token_acesso

router = APIRouter()

# GET Logado
@router.get("/logado", response_model=UsuarioSchemaBase)
def get_logado(usuario_logado: UsuarioModel = Depends(get_current_user)):
    return usuario_logado


# POST / Sign-up
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session)):
    novo_usuario: UsuarioModel = UsuarioModel(
        nome=usuario.nome, 
        sobrenome=usuario.sobrenome, 
        email=usuario.email, 
        senha=gerar_hash_senha(usuario.senha), 
        isadmin=usuario.isadmin)
    
    try:
        async with db as session:
            session.add(novo_usuario)
            await session.commit()

            return novo_usuario

    except IntegrityError:
        raise HTTPException(detail=f"Erro ao inserir usuário", status_code=status.HTTP_403_FORBIDDEN)
        

# GET Usuarios
@router.get("/", response_model=List[UsuarioSchemaBase])
async def get_usuarios(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel)
        result = await session.execute(query)
        usuarios: List[UsuarioSchemaBase] = result.scalars().unique().all()

        return usuarios

# Get usuario por id
@router.get("/{id_usuario}", response_model=UsuarioSchemaArtigos, status_code=status.HTTP_200_OK)
async def get_usuario(id_usuario: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id_usuario)
        result = await session.execute(query)

        usuario: UsuarioSchemaArtigos = result.scalars().unique().one_or_none()

        if usuario:
            return usuario
        
        raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)


# PUT Usuario
@router.put("/{id_usuario}", response_model=UsuarioSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_usuario(id_usuario: int, usuario: UsuarioSchemaUp, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id_usuario)
        result = await session.execute(query)

        usuario_up: UsuarioSchemaBase = result.scalars().unique().one_or_none()

        if usuario_up:
            if usuario.nome:
                usuario_up.nome = usuario.nome

            if usuario.sobrenome:
                usuario_up.sobrenome = usuario.sobrenome

            if usuario.email:
                usuario_up.email = usuario.email

            if usuario.isadmin:
                usuario_up.isadmin = usuario.isadmin

            if usuario.senha:
                usuario_up.senha = gerar_hash_senha(usuario.senha)
            
            await session.commit()

            return usuario_up
        
        raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)


# DELETE usuario
@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(id_usuario: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UsuarioModel).filter(UsuarioModel.id == id_usuario)
        result = await session.execute(query)

        usuario_del: UsuarioSchemaArtigos = result.scalars().unique().one_or_none()

        if usuario_del:
            await session.delete(usuario_del)
            await session.commit()

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
        raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)


# POST login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    usuario = await autenticar(email=form_data.username, senha=form_data.password, db=db)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados de acesso incorretos.")
    return JSONResponse(content={"access_token": criar_token_acesso(sub=usuario.id), "token_type": "bearer"}, status_code=status.HTTP_200_OK)  
    