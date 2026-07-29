# Solution HUB

Solution HUB is a software designed for the technical archiving of errors or problems encountered during daily work.

**Perché è utile?**
* Makes solutions to previously encountered problems easily accessible.
* Speeds up diagnosis times thanks to guided troubleshooting.
* Allows you to share acquired knowledge with other collaborators who may encounter the same problems.

**Note**
* Efficiency and ease of use depend on users entering data appropriately.
* Officially entering data will make the data search system less efficient.

## Installation
For installation, we recommend following these steps:
* Copy the repository locally to your machine
* ​​Open the newly copied project folder with your preferred IDE
* Select the "_main.py_" file and paste the following line of code into the terminal to create the executable:

```python
python -m PyInstaller --onefile --noconsole --clean --splash main.py
```

## Functioning
The main features of the software are briefly explained below:
1. **Main window**
   * When you open the application, a window will appear with three distinct areas:
     * **Left**: Area for inserting and saving new records
     * **Top**: Area for searching for records and selecting search filters
     * **Right**: Area for viewing the table with all saved records

2. **Inserting a new record**
   * To insert a new record, you must fill in the following fields:
     * **Machine type**: This is a list from which you can select the area where the problem occurred.
     * **Subject**: Component with which the problem was encountered
     * **Description**: Field for entering a description of the problem
     * **Solution**: Field for entering a description of the solution adopted
     * **"_Save_" button**: Allows you to save the entered data in the database

3. **Attach files to the record**
   * When you press the "_Save_" button, you will be given the option to attach a file to the record.
   * The file can be an _image, a docx, pdf, txt, md,_ etc. file, which adds information about what happened.
   * If you do not wish to attach any files, simply click "_No_" in the window that appears.

4. **Searching for a record**
   * The search bar allows you to search for records within the database.
   * The search is based on the "_Subject_", "_Problem_" and "_Solution_" fields and is case-insensitive.
   * The text search can be implemented with **_filters_**:
     * Filters can be selected using the drop-down menu to the right of the search bar.
     * You can search by applying only the filters and leaving the search field blank.

5. **Viewing a record**
   * Selecting a record in the table opens a window that displays the details of what's saved for that record. There are two options:
     * Click the blue "Open Detail" button at the bottom
     * Double-click the record
   * A window will open with several buttons available, in addition to the record:
     * Edit Record
     * Add/Edit Attachment
     * Delete Record
     * Close Window

6. **Editing a record**
   * From the detail window, you can edit the selected record.
   * When you press the button, the record information will be displayed in the left area of ​​the application.
   * At this point, you can edit the record's contents and save the changes (the procedure is the same as for inserting a new record).

7. **Deleting a record**
   * From the detail window, you can **permanently delete** the selected record.
   * When you press the button, not only the record but also any attached document will be deleted.

## Support:
If you encounter any problems during operation or have suggestions for improvement, please do not hesitate to contact me [here](https://github.com/riccardomerola/SolutionHub/issues/new/choose).