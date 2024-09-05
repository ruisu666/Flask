# Vehicle Management System

## To run this program, you need to follow a set of requirements first:

### 1. Python
   - Make sure Python is installed on your system. You can download it from [here](https://www.python.org/downloads/).
   - Check Python version by running:
     ```bash
     python --version
     ```

### 2. XAMPP
   - Download and install XAMPP to set up Apache and MySQL for the database. You can get it from [here](https://www.apachefriends.org/index.html).

### 3. Import the Database to PhpMyAdmin
   - Open PhpMyAdmin and import the provided SQL database file.

### 4. Any IDE or Text Editor (I use VS Code)
   - VS Code can be downloaded from [here](https://code.visualstudio.com/).

### 5. Create a Virtual Environment and Install Dependencies
   To ensure the project runs correctly, you need to create a Python virtual environment and install the necessary dependencies.

   #### Steps:
   1. **Navigate to the project folder**:
      ```bash
      cd vms
      ```

   2. **Create a virtual environment**:
      - On Windows:
        ```bash
        python -m venv myenv
        ```

   3. **Activate the virtual environment**:
      - On Windows:
        ```bash
        myenv\Scripts\activate
        ```

   4. **Install the dependencies from `requirements.txt`**:
      ```bash
      pip install -r requirements.txt
      ```

   5. **Run the Flask app**:
      - Run the application with:
        ```bash
        python app.py
        ```

That's it! The app should now be running locally on your system.
