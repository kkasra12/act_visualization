import os
import pickle
from typing import Optional

from openai import OpenAI

try:
    from config import API_KEY
    os.environ["OPENAI_API_KEY"] = API_KEY
except ImportError:
    API_KEY = os.environ.get("OPENAI_API_KEY", "")
    print(
        "API_KEY is not provided in config.py, using OPENAI_API_KEY environment variable"
        " instead.\nIf you want to use config.py, please set API_KEY variable in config.py"
        "\nWhitout API_KEY, you can only use the available classification (already saved in classifier.pkl)"
        "\nIf you want to make new classification, please set API_KEY in config.py or set OPENAI_API_KEY environment variable"
    )


class CacheDict:
    def __init__(self, address: str | os.PathLike) -> None:
        self.address = address
        if os.path.isfile(address):
            with open(address, "rb") as f:
                self.dict = pickle.load(f)
        else:
            self.dict = {}

    def __getitem__(self, key: str) -> str:
        return self.dict[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.dict[key] = value
        with open(self.address, "wb") as f:
            pickle.dump(self.dict, f)

    def __contains__(self, key: str) -> bool:
        return key in self.dict

    def get(self, key: str, default: str) -> str:
        return self.dict.get(key, default)

    def __repr__(self) -> str:
        return repr(self.dict)

    def __str__(self) -> str:
        return str(self.dict)

    def values(self):
        return self.dict.values()


class Classifier:
    class_dict: CacheDict | dict[str, str]

    def __init__(self, initil_classes: list[str], cache_file: Optional[str] = None):
        self.classes = initil_classes
        self.prompt = (
            "You will get a sentence from AI Act document. Please classify it as one of the following categories: \n{}\n\n"
            "if you think a new class is needed, please write as a new class\n"
            "note that your output should be a single word\n\n"
        )
        # self.client = OpenAI(api_key=API_KEY)
        self.client = OpenAI()
        if cache_file is not None:
            self.class_dict = CacheDict(cache_file)
        else:
            self.class_dict = {}

    def sent_classify(
        self,
        sentence: str,
    ) -> tuple[str | None, int | float]:
        prompt = self.prompt.format("\n".join(self.classes))
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": sentence},
            ],
        )
        if response.usage is not None:
            usage: float | int = response.usage.total_tokens
        else:
            usage = float("nan")

        return response.choices[0].message.content, usage

    def text_classify(self, text: list[str], progress_bar=None):
        """
        text: list of sentences
        cache_file: if not None then the result not saved to cache_file
        otherwise the result is saved to cache_file
        cache_file shold be a pickle file which contains a dictionary wich keys are sentences and values are classes
        """
        if progress_bar is None:

            def progress_bar(x):
                return x

        sum_of_tokens: float | int = 0
        for sent in progress_bar(text):
            if sent in self.class_dict:
                class_ = self.class_dict[sent]
                tokens: int | float = 0
            else:
                class_, tokens = self.sent_classify(sent)  # type: ignore

            if isinstance(class_, str):
                class_ = class_.lower()
                if class_ not in self.classes:
                    self.classes.append(class_)

                self.class_dict[sent] = class_
            sum_of_tokens += tokens

        return sum_of_tokens


if __name__ == "__main__":
    classifier = Classifier(["good", "very good"])
    st = classifier.text_classify(["this is good", "this is very good", "this is bad"])
    print(classifier.class_dict)
    print(st)
