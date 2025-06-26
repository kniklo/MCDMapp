# 🧠 MCDM Decision Support System (FAHP-based)

A Flask-based decision support system (DSS) implementing the **Fuzzy Analytic Hierarchy Process (FAHP)** for evaluating alternatives (e.g., products).  
Users can define criteria and alternatives, enter expert judgments, and receive automated analysis results.

---

## Features

- ✅ Full FAHP implementation: fuzzification, consistency check, weight calculation  
- ✅ SQLAlchemy + MySQL support  
- ✅ Modular Flask architecture  
- ✅ User authentication, task management, expert workflows  
- ✅ AJAX support for dynamic interactions  

---

## Project Structure

MCDMapp/
├── app/
│ ├── services/ # FAHP logic: fuzzification, consistency check, weights
│ ├── static/ # CSS, JS, images, fonts
│ ├── templates/ # Jinja2 HTML templates
│ ├── tests/ # Unit tests for FAHP and Flask routes
│ ├── init.py 
│ ├── forms.py # WTForms 
│ ├── models.py # SQLAlchemy models (users, tasks, criteria, etc.)
│ └── routes.py # Flask routes and main logic
├── config.py 
├── dmapp.py # Entry point for running the app
├── .env.example 
├── requirements.txt 
├── Dockerfile 
├── docker-compose.yml 
└── README.md 


---

## ⚙️ Getting Started

Make sure you have [Docker](https://www.docker.com/) and [Docker Compose]([https://docs.docker.com/compose/](https://docs.docker.com/compose/install/)) installed.

### 🧪 Run the project

```bash
git clone https://github.com/kniklo/MCDMapp.git
cd MCDMapp
docker compose up
```

The app will be available at: http://localhost:8000.

---

# How to use

1. We introduce a short name and the purpose of choosing between items.
![image](https://github.com/user-attachments/assets/b4b3476f-adaf-406c-9940-7a7a49a70ca6)

2. First, we enter the products we choose between (**alternatives**), and then the **criteria** by which we evaluate the product's preference for us. (at least 2)
![image](https://github.com/user-attachments/assets/c176d3b5-cbf0-4bf4-a5bb-7d303b4e6aae)

3. Now we can select our task and analyze it (or leave it for others to analyze).
![image](https://github.com/user-attachments/assets/d02feaa0-5da6-425a-b0ca-314848a9e417)

4. First, we rank the criteria **relative to each other** based on how important they are **for us** in this specific decision.

> 💡 In this example, my top priority is **not to include harmful ingredients**, so I assign **10 points** to the first criterion.  
> Next comes the **price**, and the last two seem equally important — but still **less important than price or bad ingredients**.

- The **greater the difference** between the numbers, the more different their importance is to you.
- ⚠️ **Note:** Do not assign all values close together — use the **full scale** to reflect real priorities!
![image](https://github.com/user-attachments/assets/2ed879ed-549c-4e3b-b2f4-a150db09157b)

5. Now we need to evaluate how good **each product is compared to the others** for **one criterion at a time**, using a scale from **1 to 10**.
![image](https://github.com/user-attachments/assets/8758a4a3-163a-4084-ac39-3a9fa2fbbf20)

This process is much easier if you already have concrete data in front of you — here, you simply add your **subjective judgments** based on that information.
> 📊 For example, let’s take a look at my Notion document where I gathered data on several products.
> ![image](https://github.com/user-attachments/assets/6ed6abbe-dd6c-4ff4-ab0d-ba12b4aded89)

#### Criterion: **Price** (the lower, the better)
| Product       | Price Score (1–10) |
|---------------|--------------------|
| IUNIK         | 10 _(lowest price)_ |
| DEAR, KLAIRS  | 4                  |
| ABIB          | 2 _(highest price)_ |
Repeat this process for the remaining criteria using the same logic.

6. Now we can clearly see **what we prioritized** in our decision-making and **which criteria mattered most** to us.
> 💡 In my case, the best choice turned out to be **ABIB**, since it received the highest overall score compared to the other products.
![image](https://github.com/user-attachments/assets/8e4bd0a7-d948-4584-b9b9-7bea111b6364)

---

👥 **Multiple Experts: Compare Opinions**
Let’s say Tom also logged into his account and analyzed the same task.  
Now, by selecting **"Detailed"**, we can view the **average evaluation across all experts**.
> 📊 As we can see, **IUNIK** is now considered the most preferred product based on combined input.
![image](https://github.com/user-attachments/assets/7083fab9-62bd-417c-9e38-d7e293c3ffca)
![image](https://github.com/user-attachments/assets/575930d0-d2de-4085-9c9e-7955da8166bf)

**View aggregation of only selected analyses**
To dive deeper into Tom’s perspective:
1. **Deselect** Alice’s analysis.
2. Click **"Summary analysis"**.
![image](https://github.com/user-attachments/assets/02c946b0-8c59-4069-9b0b-5c3c2e58cfea)

> 🧠 From Tom’s results, we can see that he prioritized **price** and **product quantity**,  
> while paying **no attention** to the quality of ingredients — either good or bad.

---

Made with ❤️ by kniklo


