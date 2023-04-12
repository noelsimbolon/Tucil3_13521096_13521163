import customtkinter


def change_appearance_mode(new_appearance_mode: str) -> None:
    """
    Changes the GUI theme
    :param new_appearance_mode: string: "dark", "light", or "system"
    """
    customtkinter.set_appearance_mode(new_appearance_mode)
