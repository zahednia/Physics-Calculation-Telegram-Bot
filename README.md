
# Physics Calculation Telegram Bot

![Banner](https://github.com/zahednia/Physics-Calculation-Telegram-Bot/blob/main/photo.jpg)  <!-- Add your image path here -->

## **Description:**
This is a **Telegram bot** designed to help users calculate physical quantities like average velocity, average acceleration, and displacement from a set of time-location data. The bot now supports **3D calculations** for position, velocity, and acceleration vectors, allowing for more detailed analysis of movement in three dimensions. Users input their time and location values, and the bot computes various physics formulas and presents the results with **visual graphs**.

🎯 **Key Features:**
- 📐 Calculates **average velocity** (`V_avg`), **average acceleration** (`A_avg`), and **overall displacement** (`S_avg`) in **3D**.
- 📊 Displays results in a clean and understandable format.
- 📈 Generates **3D graphs** for time vs. position, average velocity, and acceleration.
- 💬 Interactive user experience using **Telegram buttons** to guide the user through the data input and calculation process.

---

## **Installation:**

### **Pre-requisites:**
1. **Python 3.10** or later.
2. Libraries:
   - `python-telegram-bot`
   - `numpy`
   - `matplotlib`

🔧 You can install the required Python libraries with the following command:
```bash
pip install python-telegram-bot numpy matplotlib
```

---

### **Steps for Installation:**

1. **Download or Clone the Repository:**
   Clone the repository to your local machine or download it as a zip file:
   ```bash
   git clone https://github.com/yourusername/Physics-Telegram-Bot.git
   ```

2. **Configure the Bot Token:**
   - Open the `config.json` file in the project directory.
   - Replace the empty string `""` with your actual **Telegram Bot token**, which you can get from [BotFather](https://core.telegram.org/bots#botfather).

   Example:
   ```json
   {
       "BOT_TOKEN": "your-telegram-bot-token-here"
   }
   ```

3. **Run the Bot:**
   After setting the bot token, you can run the bot script.

   - On **Linux**:
     ```bash
     python3 bot.py
     ```

   - On **Windows**:
     Open Command Prompt or PowerShell and run:
     ```bash
     python bot.py
     ```

4. **Running the Bot:**
   Once the bot is running, it will be available for use through Telegram. You can send time and location data, and it will respond with the calculated results and graphs.

---

## **How to Use the Bot:**

1. **Start the Bot:**
   Open **Telegram** and search for your bot by its username or directly through the bot link. Send `/start` to begin the interaction.

2. **Data Input:**
   The bot will ask for the following information:
   - 🕒 **Time (T)**: Enter the time at which a measurement was taken.
   - 📍 **Location (X)**: Enter the 3D location (position) corresponding to the time.

   You can add multiple points for more accurate calculation. After entering at least two points, you can proceed to the calculations.

3. **Perform Calculations:**
   Once enough data points are entered, the bot will perform the following calculations:
   - **Average Velocity (V_avg)**: Calculates the average velocity between each pair of points.
   - **Average Acceleration (A_avg)**: Computes the average acceleration between each pair of velocities.
   - **Overall Displacement (S_avg)**: Computes the total displacement between the first and last points.

   The bot will also generate a graph with time vs. position, average velocity, and average acceleration in 3D.

4. **Sample Input & Output:**

   **Input:**
   ```
   Time: 0   Location: [5, 1, 1]
   Time: 1   Location: [7, 8, 1]
   Time: 2   Location: [12, 23, 1]
   Time: 3   Location: [23, 32, 1]
   ```

   **Output:**
   ```
   ✅ **Calculations Completed:**

   1️⃣ **Average Velocity between each pair of points:**
   V_avg = ΔX / ΔT
   Results: V_avg = [[2.0, 7.0, 0.0], [2.5, 7.5, 0.0]]

   2️⃣ **Average Acceleration between velocities:**
   A_avg = ΔV / ΔT
   Results: A_avg = [[0.3333, 0.3333, 0.0]]

   3️⃣ **Overall Displacement (S_avg):**
   S_avg = ΔX / ΔT
   S_avg = ([12. 23. 1.] - [5. 1. 1.]) / (3.0 - 0.0) = 4.0 / 3.0 = [2.3333 7.3333 0.    ]

   🔹 **Summary:**
   V_avg: [2.0, 7.0, 0.0]
   A_avg: [0.3333, 0.3333, 0.0]
   S_avg: [2.3333, 7.3333, 0.0]
   ```

5. **Graphs:**
   After the calculations, the bot will provide a graphical representation of:
   - 📍 Time vs. Position (3D)
   - ⚡ Time vs. Average Velocity (3D)
   - 📉 Time vs. Average Acceleration (3D)

---

## **Running the Bot on Linux:**
1. Install Python and necessary libraries:
   ```bash
   sudo apt install python3 python3-pip
   pip install python-telegram-bot numpy matplotlib
   ```

2. Clone the repository and configure the token in `config.json`:
   ```bash
   git clone https://github.com/yourusername/Physics-Telegram-Bot.git
   cd Physics-Telegram-Bot
   ```

3. Run the bot:
   ```bash
   python3 bot.py
   ```

---

## **Running the Bot on Windows:**
1. Install Python and necessary libraries:
   - Download Python from [python.org](https://www.python.org/downloads/).
   - Install necessary libraries:
     ```bash
     pip install python-telegram-bot numpy matplotlib
     ```

2. Clone the repository or download it, then configure the token in `config.json`.

3. Run the bot:
   ```bash
   python bot.py
   ```

---

## **Contributing:**

Feel free to fork this repository and contribute by improving features, fixing bugs, or adding new functionality. If you have any suggestions or issues, open a pull request or create an issue on GitHub.

---

### **License:**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### **Contact:**
For any further questions or suggestions, feel free to reach out at [Linkedin](https://www.linkedin.com/in/kourosh-zahednia/).
