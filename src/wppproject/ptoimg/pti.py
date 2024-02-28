import datetime
import os
import random
import webbrowser
import cv2
from openai import OpenAI
import requests

class ImageGenerator:
    def __init__(self, client = None, art_style = None, use_OpenAI = True):
        if not client and use_OpenAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                client = OpenAI(api_key=api_key)

        self.client:OpenAI = client
        self._poem = []
        self._title = ""
        self._author = ""
        self.art_style = art_style

    @property
    def poem(self):
        return self._poem
    
    @poem.setter
    def poem(self, poem: list):
        """Set the poem to be used."""
        _p = []
        if isinstance(poem, str):
            _p = poem.split("\n")
        elif len(poem) !=0 and isinstance(poem[0], dict):
            _p = poem[0]['lines']
            _t = poem[0]['title']
            _a = poem[0]['author']
            self._title = _t
            self._author = _a
        else:
            _p = poem
        self._poem = _p

    @property
    def author(self):
        return self._author
    
    @author.setter
    def author(self, author: str):
        self._author = author
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def art_style(self):
        return self._art_style
    
    @art_style.setter
    def art_style(self, style: str):
        self._art_style = style
    
    
    def load_image(self):
        """Load an image from a file."""
        # try to select a random image from data folder
        files = os.listdir("data")
        files = [f for f in files if f.endswith(".png")]
        if len(files) > 0:
            # randomly select an image
            random.shuffle(files)
            img_path = os.path.join("data", files[0])
            # load the image
            self.img = cv2.imread(img_path)
            return
        else:
            raise ValueError("No image found in data folder.")
    

    def generate_image(self):
        """Generate an image based on a poem."""
        if not self.client:
            # try to select a random image from data folder
            files = os.listdir("data")
            files = [f for f in files if f.endswith(".png")]
            if len(files) > 0:
                img_path = os.path.join("data", files[0])
                # load the image
                self.img = cv2.imread(img_path)
                return

            else:
                raise ValueError("No OpenAI Key set and no image found in data folder.")

        def _poem_to_promt() -> str:
            """Convert a poem to a prompt."""
            poem = self.poem   
            # print(type(poem))         
            poem = " ".join(poem)
            poem = poem.replace("\n", " ")

            response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt = f"Write one sentence description for an image, to represent and depict the following poem: \n{poem} \n\nNo direct reference to the poem is necacary. Dont use Words, that may be violating terms of service. The image should be in a {self.art_style} style\n\nImage description:",
            max_tokens=100
            )
            # print(response.choices[0].text)

            return response.choices[0].text
        
        def _generate_image(prompt: str) -> str:
            """Generate an image based on a prompt."""
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        
        def _download_image():
            """Download an image from the URL."""
            url = self.img_url
            response = requests.get(url)
            # save to data folder as date-time.png
            time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            with open(f"data/{time}.png", "wb") as file:
                file.write(response.content)
            return cv2.imread(f"data/{time}.png")
                
        self.prompt = _poem_to_promt()
        self.img_url = _generate_image(self.prompt)
        self.img = _download_image()

    
    
    def insert_poem(self) -> cv2:
        """Insert a poem into an image."""
        # insert the poem into the image
        # line by line

        def _insert_text(line, position, img, front_color = (255,255,255), back_color = (0, 0, 0), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, thickness=3, line_type=cv2.LINE_AA, right_align=False):
            """Insert text into an image."""
            text_size = cv2.getTextSize(line, font, font_scale, thickness)
            if right_align:
                position = (position[0] - text_size[0][0], position[1])
            # insert shadow
            cv2.putText(img, line, position, font, font_scale, back_color, thickness+15, line_type)
            cv2.putText(img, line, position, font, font_scale, front_color, thickness, line_type)
            return img

        img = self.img

        if len(self.poem) == 0:
            raise ValueError("No poem found.")
        poem = self.poem
        
        if len(self._title) > 0:
            img = _insert_text(self._title, (70, 90), img, front_color=(255, 255, 255), back_color=(0, 0, 0), font_scale=2.2, thickness=6, right_align=False)
        if len(self._author) > 0:
            img = _insert_text(self._author, (70, 150), img, front_color=(255, 255, 255), back_color=(0, 0, 0), font_scale=1.2, thickness=3, right_align=False)


        # devide the poem to two columns
        half = len(self.poem) // 2
        if half != 0:
            left = self.poem[:half][::-1]
            right = self.poem[half:][::-1]

            poem = zip(left, right)

        img_size = img.shape
        # insert the poem
        l_offset, r_offset = 70, img_size[1] - 70
        for i, (left, right) in enumerate(poem): 
            img = _insert_text(left.strip(), (l_offset, img_size[0] - 50 - 50*i), img)
            img = _insert_text(right.strip(), (r_offset, img_size[0] - 50 - 50*i), img, right_align=True)

        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        cv2.imwrite(f"data/poem_{time}.png", img)
        return img
    
    def speak_poem(self):
        """Speak the poem."""
        client = self.client
        title = self.title
        author = self.author
        introduction = f"{title}  ...   by {author}....... "
        poem = self.poem
        poem = " ".join(poem)
        poem = poem.replace("\n", " ")
        poem = poem.replace("-", " ")
        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        path = f"data/poem_{time}.mp3"
        response = client.audio.speech.create(model="tts-1", voice="onyx", input=introduction+poem)

        response.stream_to_file(path)
        abs_path = os.path.abspath(path)
        webbrowser.open(abs_path)

            

if __name__ == "__main__":
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise KeyError
        print(f"API Key: {api_key}")
    except KeyError:    
        print("Please set the environment variable OPENAI_API_KEY.")
        exit(1)

    ig = ImageGenerator()

    poem = [
        "Two roads diverged in a yellow wood,",
        "And sorry I could not travel both",
        "And be one traveler, long I stood",
        "And looked down one as far as I could",
        "",

        "Then took the other, as just as fair,",
        "And having perhaps the better claim",
        "Because it was grassy and wanted wear,",
        "Though as for that the passing there",
        "Had worn them really about the same,",
        "",

        "And both that morning equally lay",
        "In leaves no step had trodden black.",
        "Oh, I kept the first for another day!",
        "Yet knowing how way leads on to way",
        "I doubted if I should ever come back.",
        "",

        "I shall be telling this with a sigh",
        "Somewhere ages and ages hence:",
        "Two roads diverged in a wood, and I,",
        "I took the one less traveled by,",
        "And that has made all the difference."
    ]

    ig.poem = poem
    ig.author = "Theodor Fontane"
    ig.title = "An Emilie"
    # ig.author = "Robert Frost"
    # ig.title = "The Road Not Taken"
    ig.generate_image()
    # ig.load_image()
    ig.insert_poem()
    print("The image has been generated and the poem has been inserted.")