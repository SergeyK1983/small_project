import asyncio

import typer
from rich import print

from src.auth.commands.create_superuser import create_superuser


app = typer.Typer()


@app.command()
def createsuperuser(
        # username: str = typer.Argument(..., help="Имя пользователя"),
        # pwd: str = typer.Argument(..., help="Пароль")
) -> None:
    username = input("Введите имя пользователя: ")
    pwd = input("Введите пароль: ")

    msg: str = asyncio.run(create_superuser(username, pwd))
    print(f"[bold green]{msg}[/bold green]")
    return


@app.command()
def hello():
    print(f"[bold green]Приветствие от Small project![/bold green]")


if __name__ == '__main__':
    app()
