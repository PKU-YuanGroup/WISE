# WISE

<p align="left">
  <a href="#🚀-quick-start"><b>Quick Start</b></a> |
  <a href=""><b>arXiv</b></a> |
</a>
  <a href="#🖊️-citation"><b>Citation</b></a> <br>
</p>

This repository is the official implementation of [WISE]([https://arxiv.org/abs](https://github.com/)). 

## 💡 News
- 2025//: We release our paper at https://arxiv.org/abs/. We have released the codes and data.

  
## 🎩Introduction

Text-to-Image (T2I) models are capable of generating high-quality artistic creations and visual content. However, existing research and evaluation standards predominantly focus on image realism and shallow text-image alignment, lacking a comprehensive assessment of complex semantic understanding and world knowledge integration in text to image generation. 
To address this challenge, we propose WISE, the first benchmark specifically designed for World Knowledge-Informed Semantic Evaluation.  WISE moves beyond simple word-pixel mapping by challenging models with 1000 meticulously crafted prompts across 25 sub-domains in cultural common sense, spatio-temporal understanding, and natural science. 
To overcome the limitations of traditional CLIP metric, we introduce WiScore, a novel quantitative metric for assessing knowledge-image alignment. Through comprehensive testing of 20 models (10 dedicated T2I models and 10 unified multimodal models) using 1,000 structured prompts spanning 25 subdomains, our findings reveal significant limitations in their ability to effectively integrate and apply world knowledge during image generation, highlighting critical pathways for enhancing knowledge incorporation and application in next-generation T2I models.

<img src="static/intro.png" alt="overview" style="zoom:80%;" />
