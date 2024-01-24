# install dependencies
to install dependencies, run `pip install -r requirements.txt`

# create slides
to create slides, run
```bash
jupyter-nbconvert --to slides main.ipynb \
 --SlidesExporter.reveal_theme=serif \
 --SlidesExporter.reveal_scroll=True \
 --SlidesExporter.reveal_transition=concave \
 --SlidesExporter.exclude_input=True \
 --SlidesExporter.reveal_number="v.h"
```

there should be a file named `main.slides.html`. open it in a browser to view the slides.


# rerun the classification
if you want to rerun the classification:
create a Python file named `config.py` and define `API_KEY`.
```bash
echo "API_KEY = <YOUR_API_KEY>" > config.py
```
2. delete the `classifier.pkl` file or change its name. Also, you can change the file name in the code (you can find it almost end of `main.ipynb`).
3. run `main.ipynb` again.


# view the slides
to see the rendered slides click [here](https://kkasra12.github.io/act_visualization/main.slides.html#/).