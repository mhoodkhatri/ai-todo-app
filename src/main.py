import sys

from src.services.task_service import TaskService
from src.ui.console import (
    display_error,
    display_menu,
    display_welcome_banner,
)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    service = TaskService()
    display_welcome_banner()

    while True:
        try:
            display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                from src.ui.console import prompt_add_task
                prompt_add_task(service)
            elif choice == "2":
                from src.ui.console import display_all_tasks
                display_all_tasks(service)
            elif choice == "3":
                from src.ui.console import prompt_update_task
                prompt_update_task(service)
            elif choice == "4":
                from src.ui.console import prompt_delete_task
                prompt_delete_task(service)
            elif choice == "5":
                from src.ui.console import prompt_toggle_task
                prompt_toggle_task(service)
            elif choice == "6":
                print("\nGoodbye! Have a productive day!")
                break
            else:
                display_error("Invalid option. Please enter a number between 1 and 6.")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye! Have a productive day!")
            break


if __name__ == "__main__":
    main()
