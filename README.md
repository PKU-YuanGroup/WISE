# WISE



This repository is the official implementation of [WISE]([[https://arxiv.org/abs](https://arxiv.org/abs/2503.07265)]((https://arxiv.org/abs/2503.07265))).   

## 💡 News 
- 2025/06/03: We have updated our code again to provide clearer, simpler, and easier evaluation! 😊
- 2025/05/24: We have collected some feedback and updated our code. If you have any questions or comments, feel free to email us at [niuyuwei04@gmail.com](mailto:niuyuwei04@gmail.com)!
- 2025/03/11: We release our paper at [https://arxiv.org/abs/wise](https://arxiv.org/abs/2503.07265).
- 2025/03/10: We have released the codes and data.
  
## 🎩Introduction

Text-to-Image (T2I) models are capable of generating high-quality artistic creations and visual content. However, existing research and evaluation standards predominantly focus on image realism and shallow text-image alignment, lacking a comprehensive assessment of complex semantic understanding and world knowledge integration in text to image generation. 
To address this challenge, we propose WISE, the first benchmark specifically designed for World Knowledge-Informed Semantic Evaluation.  WISE moves beyond simple word-pixel mapping by challenging models with 1000 meticulously crafted prompts across 25 sub-domains in cultural common sense, spatio-temporal understanding, and natural science. 
To overcome the limitations of traditional CLIP metric, we introduce WiScore, a novel quantitative metric for assessing knowledge-image alignment. Through comprehensive testing of 20 models (10 dedicated T2I models and 10 unified multimodal models) using 1,000 structured prompts spanning 25 subdomains, our findings reveal significant limitations in their ability to effectively integrate and apply world knowledge during image generation, highlighting critical pathways for enhancing knowledge incorporation and application in next-generation T2I models.

<img src="assets/intro.png" alt="overview" style="zoom:80%;" />

## 📖WISE Eval
<img src="assets/examples.png" alt="overview" style="zoom:80%;" />

1.  **Prompt Generation:**  We meticulously crafted 1000 prompts across 25 sub-domains within Cultural Common Sense, Spatio-temporal Reasoning, and Natural Science.  
2.  **Image Generation:** Each prompt was fed to 20 different Text-to-Image (T2I) models (10 dedicated T2I models and 10 unified multimodal models) to generate corresponding images.  
3.  **GPT-4o Evaluation:** For each generated image, we employed **GPT-4o-2024-05-13** (with specified instructions detailed in the paper) to independently assess and score each aspect (Consistency, Realism, and Aesthetic Quality) on a scale from 0 to 2.  GPT-4o acts as a judge, providing objective and consistent scoring.
4.  **WiScore Calculation:**  Finally, we calculated the WiScore for each image based on the GPT-4o scores and the defined weights, providing a comprehensive assessment of the model's ability to generate world knowledge-informed images.


<img src="assets/framework_2.jpg" alt="overview" style="zoom:80%;" />
WiScore assesses Text-to-Image models using three key components:

*   **Consistency:** How accurately the image matches the prompt's content and relationships.
*   **Realism:** How believable and photorealistic the image appears.
*   **Aesthetic Quality:** How visually appealing and artistically well-composed the image is.

**WiScore Calculation:**

`WiScore = (0.7 * Consistency + 0.2 * Realism + 0.1 * Aesthetic Quality) /2`  

The **Overall WiScore** is a weighted sum of six categories:  

`Overall WiScore = (0.4 * Cultural + 0.167 * Time + 0.133 * Space + 0.1 * Biology + 0.1 * Physics + 0.1 * Chemistry)`

**Prompt rewrite analysis:**

<img src="assets/Table2.png" alt="overview" style="zoom:80%;" />

WiScore on rewritten prompts of different models. These prompts were simplified from the original WISE benchmark using GPT-4o (e.g., "The plant often gifted on Mother’s Day" to "Carnation"). Green ball indicates score increase after rewriting; red ball indicates score decrease. A smaller difference indicates that the model has a stronger ability to model world knowledge. This indicator excludes the influence of the generation quality itself.

## Usage Guide

---

To evaluate using **GPT-4o-2024-05-13**, follow these steps:

### 1. Evaluate with GPT-4o-2024-05-13

First, set the `IMAGE_DIR` variable to the directory where your model's generated images are saved. The image names should be in the format `1-1000.png`.

```bash
IMAGE_DIR="path/to/your_image_output_dir" # Directory where model-generated images are saved, e.g., 1-1000.png
```

Then, run the `gpt_eval.py` script for each category. Remember to replace `""` with your actual API key.

```bash
python gpt_eval.py \
    --json_path data/cultural_common_sense.json \
    --output_dir ${IMAGE_DIR}/Results/cultural_common_sense \
    --image_dir ${IMAGE_DIR} \
    --api_key "" \
    --model "gpt-4o-2024-05-13" \
    --result_full ${IMAGE_DIR}/Results/cultural_common_sense_full_results.json \
    --result_scores ${IMAGE_DIR}/Results/cultural_common_sense_scores_results.jsonl \
    --max_workers 96

python gpt_eval.py \
    --json_path data/spatio-temporal_reasoning.json \
    --output_dir ${IMAGE_DIR}/Results/spatio-temporal_reasoning \
    --image_dir ${IMAGE_DIR} \
    --api_key "" \
    --model "gpt-4o-2024-05-13" \
    --result_full ${IMAGE_DIR}/Results/spatio-temporal_reasoning_results.json \
    --result_scores ${IMAGE_DIR}/Results/spatio-temporal_reasoning_results.jsonl \
    --max_workers 96

python gpt_eval.py \
    --json_path data/natural_science.json \
    --output_dir ${IMAGE_DIR}/Results/natural_science \
    --image_dir ${IMAGE_DIR} \
    --api_key "" \
    --model "gpt-4o-2024-05-13" \
    --result_full ${IMAGE_DIR}/Results/natural_science_full_results.json \
    --result_scores ${IMAGE_DIR}/Results/natural_science_scores_results.jsonl \
    --max_workers 96
```

### 2. Calculate Scores

After running the evaluations, use `Calculate.py` to compute the scores.

```bash
python Calculate.py \
    "${IMAGE_DIR}/Results/cultural_common_sense_scores_results.jsonl" \
    "${IMAGE_DIR}/Results/natural_science_scores_results.jsonl" \
    "${IMAGE_DIR}/Results/spatio-temporal_reasoning_results.jsonl" \
    --category all
```

---

### Important Notes!

* **GPT Version**: Please ensure you use **`gpt-4o-2024-05-13`** for evaluation.
* **Breakpoint Retesting**: Our `gpt_eval.py` supports resuming from breakpoints. If your evaluation encounters an error midway, simply **re-run the script**.
* **Categorized Score Calculation**: `Calculate.py` supports calculating scores by category. You can change the `--category` parameter to specify which categories to calculate (e.g., `--category culture` or `--category all`).

---


## 🏆 Leaderboard

**Normalized WiScore of different models**
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
<table>
    <thead>
        <tr>
            <th colspan="8" class="lightyellow">Dedicated T2I</th>
        </tr>
        <tr>
            <th>Model</th>
            <th>Cultural</th>
            <th>Time</th>
            <th>Space</th>
            <th>Biology</th>
            <th>Physics</th>
            <th>Chemistry</th>
            <th><strong>Overall</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>FLUX.1-dev</td>
            <td>0.48</td>
            <td><strong>0.58</strong></td>
            <td><strong>0.62</strong></td>
            <td>0.42</td>
            <td>0.51</td>
            <td><strong>0.35</strong></td>
            <td><strong>0.50</strong></td>
        </tr>
        <tr>
            <td>FLUX.1-schnell</td>
            <td>0.39</td>
            <td>0.44</td>
            <td>0.50</td>
            <td>0.31</td>
            <td>0.44</td>
            <td>0.26</td>
            <td>0.40</td>
        </tr>
        <tr>
            <td>PixArt-Alpha</td>
            <td>0.45</td>
            <td>0.50</td>
            <td>0.48</td>
            <td><strong>0.49</strong></td>
            <td><strong>0.56</strong></td>
            <td>0.34</td>
            <td>0.47</td>
        </tr>
        <tr>
            <td>playground-v2.5</td>
            <td><strong>0.49</strong></td>
            <td>0.58</td>
            <td>0.55</td>
            <td>0.43</td>
            <td>0.48</td>
            <td>0.33</td>
            <td>0.49</td>
        </tr>
        <tr>
            <td>SD-v1-5</td>
            <td>0.34</td>
            <td>0.35</td>
            <td>0.32</td>
            <td>0.28</td>
            <td>0.29</td>
            <td>0.21</td>
            <td>0.32</td>
        </tr>
        <tr>
            <td>SD-2-1</td>
            <td>0.30</td>
            <td>0.38</td>
            <td>0.35</td>
            <td>0.33</td>
            <td>0.34</td>
            <td>0.21</td>
            <td>0.32</td>
        </tr>
        <tr>
            <td>SD-XL-base-0.9</td>
            <td>0.43</td>
            <td>0.48</td>
            <td>0.47</td>
            <td>0.44</td>
            <td>0.45</td>
            <td>0.27</td>
            <td>0.43</td>
        </tr>
        <tr>
            <td>SD-3-medium</td>
            <td>0.42</td>
            <td>0.44</td>
            <td>0.48</td>
            <td>0.39</td>
            <td>0.47</td>
            <td>0.29</td>
            <td>0.42</td>
        </tr>
        <tr>
            <td>SD-3.5-medium</td>
            <td>0.43</td>
            <td>0.50</td>
            <td>0.52</td>
            <td>0.41</td>
            <td>0.53</td>
            <td>0.33</td>
            <td>0.45</td>
        </tr>
        <tr>
            <td>SD-3.5-large</td>
            <td>0.44</td>
            <td>0.50</td>
            <td>0.58</td>
            <td>0.44</td>
            <td>0.52</td>
            <td>0.31</td>
            <td>0.46</td>
        </tr>
    </tbody>
    <thead>
        <tr>
            <th colspan="8" class="softblue">Unify MLLM</th>
        </tr>
        <tr>
            <th>Model</th>
            <th>Cultural</th>
            <th>Time</th>
            <th>Space</th>
            <th>Biology</th>
            <th>Physics</th>
            <th>Chemistry</th>
            <th><strong>Overall</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>GPT4o</td>
            <td><strong>0.81</strong></td>
            <td><strong>0.71</strong></td>
            <td><strong>0.89</strong></td>
            <td><strong>0.83</strong></td>
            <td><strong>0.79</strong></td>
            <td><strong>0.74</strong></td>
            <td><strong>0.80</strong></td>
        </tr>
        <tr>
            <td>Qwen-Image</td>
            <td>0.67</td>
            <td>0.67</td>
            <td>0.80</td>
            <td>0.62</td>
            <td>0.79</td>
            <td>0.41</td>
            <td>0.67</td>
        </tr>      
        <tr>
            <td>BAGEL</td>
            <td>0.44</td>
            <td>0.55</td>
            <td>0.68</td>
            <td>0.44</td>
            <td>0.60</td>
            <td>0.39</td>
            <td>0.52</td>
        </tr>
        <tr>
            <td>UniWorld-V1</td>
            <td>0.53</td>
            <td>0.55</td>
            <td>0.73</td>
            <td>0.45</td>
            <td>0.59</td>
            <td>0.41</td>
            <td>0.55</td>
        </tr>      
        <tr>
            <td>MetaQuery-XL</td>
            <td>0.56</td>
            <td>0.55</td>
            <td>0.62</td>
            <td>0.49</td>
            <td>0.63</td>
            <td>0.41</td>
            <td>0.55</td>
        </tr>
        <tr>
            <td>Liquid</td>
            <td>0.38</td>
            <td>0.42</td>
            <td>0.53</td>
            <td>0.36</td>
            <td>0.47</td>
            <td>0.30</td>
            <td>0.41</td>
        </tr>
        <tr>
            <td>Emu3</td>
            <td>0.34</td>
            <td>0.45</td>
            <td>0.48</td>
            <td>0.41</td>
            <td>0.45</td>
            <td>0.27</td>
            <td>0.39</td>
        </tr>
        <tr>
            <td>Harmon-1.5B</td>
            <td>0.38</td>
            <td>0.48</td>
            <td>0.52</td>
            <td>0.37</td>
            <td>0.44</td>
            <td>0.29</td>
            <td>0.41</td>
        </tr> 
        <tr>
            <td>Janus-1.3B</td>
            <td>0.16</td>
            <td>0.26</td>
            <td>0.35</td>
            <td>0.28</td>
            <td>0.30</td>
            <td>0.14</td>
            <td>0.23</td>
        </tr>
        <tr>
            <td>JanusFlow-1.3B</td>
            <td>0.13</td>
            <td>0.26</td>
            <td>0.28</td>
            <td>0.20</td>
            <td>0.19</td>
            <td>0.11</td>
            <td>0.18</td>
        </tr>
        <tr>
            <td>Janus-Pro-1B</td>
            <td>0.20</td>
            <td>0.28</td>
            <td>0.45</td>
            <td>0.24</td>
            <td>0.32</td>
            <td>0.16</td>
            <td>0.26</td>
        </tr>
        <tr>
            <td>Janus-Pro-7B</td>
            <td>0.30</td>
            <td>0.37</td>
            <td>0.49</td>
            <td>0.36</td>
            <td>0.42</td>
            <td>0.26</td>
            <td>0.35</td>
        </tr>
        <tr>
            <td>Orthus-7B-base</td>
            <td>0.07</td>
            <td>0.10</td>
            <td>0.12</td>
            <td>0.15</td>
            <td>0.15</td>
            <td>0.10</td>
            <td>0.10</td>
        </tr>
        <tr>
            <td>Orthus-7B-instruct</td>
            <td>0.23</td>
            <td>0.31</td>
            <td>0.38</td>
            <td>0.28</td>
            <td>0.31</td>
            <td>0.20</td>
            <td>0.27</td>
        </tr>
        <tr>
            <td>show-o</td>
            <td>0.28</td>
            <td>0.36</td>
            <td>0.40</td>
            <td>0.23</td>
            <td>0.33</td>
            <td>0.22</td>
            <td>0.30</td>
        </tr>
        <tr>
            <td>show-o-512</td>
            <td>0.28</td>
            <td>0.40</td>
            <td>0.48</td>
            <td>0.30</td>
            <td>0.46</td>
            <td><strong>0.30</strong></td>
            <td>0.35</td>
        </tr>
        <tr>
            <td>vila-u-7b-256</td>
            <td>0.26</td>
            <td>0.33</td>
            <td>0.37</td>
            <td>0.35</td>
            <td>0.39</td>
            <td>0.23</td>
            <td>0.31</td>
        </tr>
    </tbody>
</table>

</body>
</html>

## Citation
```
@article{niu2025wise,
  title={WISE: A World Knowledge-Informed Semantic Evaluation for Text-to-Image Generation},
  author={Niu, Yuwei and Ning, Munan and Zheng, Mengren and Jin, Weiyang and Lin, Bin and Jin, Peng and Liao, Jiaqi and Ning, Kunpeng and Feng, Chaoran and Zhu, Bin and Yuan, Li},
  journal={arXiv preprint arXiv:2503.07265},
  year={2025}
}
```


## 📧 Contact
If you have any questions, feel free to contact Yuwei Niu with niuyuwei04@gmail.com

## Recommendation

If you're interested in the Unify model, [Purshow/Awesome-Unified-Multimodal](https://github.com/Purshow/Awesome-Unified-Multimodal) is one of the most comprehensive resources for papers, code, and other materials related to unified multimodal models.

