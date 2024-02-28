import os
from poetry_client.api import PoetryDB
from ptoimg.pti import ImageGenerator
import cv2
import toml

def show_image(img: cv2.imread):
    """Display an image in a window."""
    cv2.imshow("Poetry Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def print_poems(poem: list):
    """Print a poem to the console."""
    for p in poem:
        print("\n" +"\033[1m" + p['title']+ "\033[0m"  + " (by " + p['author'] + ")\n\n" + "\n".join(p['lines'])+"\n")

def load_config() -> dict:
    with open("src/wppproject/config.toml", "r") as f:
        config = toml.load(f)
    return config

def main():
    print ("Welcome to the poetry image generator!")
    while True:
        # read imagesytle from toml file
        config = load_config()
        db_url = config["poetry"]["db_url"]
        art_style = config["artwork"]["style"]
        use_openai = config["artwork"]["use_openai"]
        option = None

        option = input("Choose from the following options:\n[1] Show a random poem\n[2] Get an poetry-image \n[3] Read a Poem\n[4] Exit\n")
     
        if option == "4":
            exit(0)
        elif option == "3":
            # get a random poem
            pdb = PoetryDB(db_url)
            try:
                poem = pdb.get_random_poems(1, min_lines=2, max_lines=40)
                print_poems(poem)
            except Exception as e:
                print(e)
                print("Failed to get a poem.")
                continue
            if os.getenv("OPENAI_API_KEY") is None:
                print("OpenAI API key not found in the environment variables. Cannot generate audio.")
                continue
            if input("\033[91m" + "Money: The use of the OpenAI API may cause charges to your account." + "\033[0m" + "\nDo you want to listen to continue? (y/n) ") == "y":
                print("Generating the audio may take a while...")
                ig = ImageGenerator(art_style=art_style, use_OpenAI=use_openai)
                ig.poem = poem
                ig.speak_poem()
                print("Audio will open in the default app.")

        elif option == "2":
            online = use_openai
            if os.getenv("OPENAI_API_KEY") is None:
                print("OpenAI API key not found.")
                online = False
            else:
                print("OpenAI API key:" + os.getenv("OPENAI_API_KEY") + " found.")
                # change color to red in the console
                print("\033[91m" + "MONEY: The use of the OpenAI API may cause CHARGEs to your account." + "\033[0m")
                ret = input("Shoud we continue in online mode? (y/n) ")
                if ret != "y":
                    online = False
    
            if not online:
                print("Switching to offline mode. Pregenerated images are reused and will not fit the Poems.")


            # get a random poem
            pdb = PoetryDB(db_url)
            try:
                poem = pdb.get_random_poems(1, min_lines=2, max_lines=20)
            except Exception as e:
                print(e)
                print("Failed to get a poem.")
                continue
            print_poems(poem)

            ig = ImageGenerator(art_style=art_style, use_OpenAI=online)
            ig.poem = poem

            if online:
                if input("Do you want to listen to the poem? (uses OpenAI API) (y/n) ") == "y":
                    print("Generating the audio may take a while...")
                    ig.speak_poem()
                    print("Audio will open in the default application.")

            if online:
                print("Generating the image may take a while...")

            ig.generate_image()

            if online:
                print("Image was generated with the Prompt: \n" + ig.prompt.strip() + "\n")

            img = ig.insert_poem()

            if input("Do you want to see the image? (y/n) ") == "y":
                # show the image
                show_image(img)

        elif option == "1":
            # get a random poem
            pdb = PoetryDB(db_url)
            try:
                poem = pdb.get_random_poems(1, min_lines=2, max_lines=20)
                print_poems(poem)
            except Exception as e:
                print(e)
                print("Failed to get a poem.")
                exit(1)

        else:
            print("Invalid option.")
            continue

