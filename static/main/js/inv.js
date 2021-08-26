/* Global vars */

/* Helper variables */
const ajaxMessageContainer = document.querySelector("#ajax_error_label");
const ajaxMessageContent = document.querySelector("#error_message");
const defaultOptionSelect = '<option value="none">Select a worksheet</option>';
const modelInsertInputsContainer = document.querySelector("#row_data_container");
const modelInsertInputsHtml = document.querySelector("#input_data_container");
const modelInsertBeforeInput = document.querySelector("#insert_row_before");
const modelInsertAfterInput = document.querySelector("#insert_row_after");
const modelInsertEndBtn = document.querySelector("#insert_row_into");
const pagenationPerPageInpt = document.querySelector("#the_pag_perpage");


const togglerButton = document.querySelector("#toggler_button");
const togglerI = document.querySelector("#toggler_i");
let currentTitlesList = [];
let modelInputsToggler = 1;

/* Sheets and files selectboxes and buttons */
const selectFileBtn = document.querySelector("#select_excelfile_btn");
const selectFileSelectBox = document.querySelector("#file_select");
const worksheetBtn = document.querySelector("#render_worksheet_btn");
const worksheetSelect = document.querySelector("#worksheet_select");

/* Table Vars*/
const tableCardContainer = document.querySelector("#table_card_container");
const sheetTableTitle = document.querySelector("#sheet_id_title");

let paginationPerPage = 10000;

const pagBtnsLimit = 5;

/* filter vars */
let filter_idlist = [];
let filter_shownlist = [];

let filter_string = "";
let addedToFilterList = [];


/* Helper functions */
function displayErrorMessage(message) {
  ajaxMessageContainer.style.display = "block";
  ajaxMessageContent.innerText = message;
  setTimeout(function(){
    ajaxMessageContainer.style.display = "none";
    ajaxMessageContent.innerText = "";
  }, 5000);
}

function pagRound(num) {
  let check0 = Number(num);
  if (isNaN(check0)){
    return num;
  }
  numcheck = num.toFixed(1);
  const strArCheck1 = numcheck.toString().split(".");
  if (strArCheck1.length <= 1) {
    return num;
  }
  const numStrArCheck2 = numcheck.toString().split(".");
  const numExtension = Number(numStrArCheck2[1]);
  if (isNaN(numExtension)){
    return num.toFixed();
  }
  if (numExtension == 0) {
    return num.toFixed();
  }
  if (numExtension > 0) {
    return Number(numStrArCheck2[0]) + 1;
  }
};

const sendPostRequest = async (url, data = {}) => {
  const response = await fetch (url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
  });
  try {
    //const newData = await response;
    return response;
  } catch(error) {
    console.log("error", error);
    // appropriately handle the error
  }
};

/* function to empty any list of inputs */
const emptyTheseInputsList = ( (inputList)=> {
  if (inputList.length == 0) {return false;}
  for (var i=0; i < inputList.length; i++) {
    if (inputList[i].value.trim() != ""){
      inputList[i].value = "";
    } else {
      continue;
    }
  }
  return true;
});


function hideDownloadInfo(infoRow, infoLink) {
  infoRow.style.display = "none";
  infoLink.innerText = "";
  infoLink.setAttribute("href", "");
  infoLink.setAttribute("download", "");
}

function showDownloadInfo(infoRow, infoLink, path) {
  infoRow.style.display = "block";
  infoLink.innerText = path;
  infoLink.setAttribute("href", path);
  infoLink.setAttribute("download", path);


}


const showAndHideInputs = ()=> {
  if (modelInputsToggler == 1) {
    modelInputsToggler = 0;
    modelInsertInputsContainer.style.display = "block";
    if (modelInsertBeforeInput.classList.contains("disabled")) {modelInsertBeforeInput.classList.remove("disabled");}
    if (modelInsertAfterInput.classList.contains("disabled")) {modelInsertAfterInput.classList.remove("disabled");}
    if (modelInsertEndBtn.classList.contains("disabled")) {modelInsertEndBtn.classList.remove("disabled");}


    if (togglerI.classList.contains("fa-eye")) {togglerI.classList.remove("fa-eye");}
    if (!togglerI.classList.contains("fa-eye-slash")) {togglerI.classList.add("fa-eye-slash");}
    return true;
  } else {
    modelInputsToggler = 1;
    modelInsertInputsContainer.style.display = "none";
    if (!modelInsertBeforeInput.classList.contains("disabled")) {modelInsertBeforeInput.classList.add("disabled");}
    if (!modelInsertAfterInput.classList.contains("disabled")) {modelInsertAfterInput.classList.add("disabled");}
    if (!modelInsertEndBtn.classList.contains("disabled")) {modelInsertEndBtn.classList.add("disabled");}
    if (!togglerI.classList.contains("fa-eye")) {togglerI.classList.add("fa-eye");}
    if (togglerI.classList.contains("fa-eye-slash")) {togglerI.classList.remove("fa-eye-slash");}
    return true;
  }
  return false;
};
togglerButton.addEventListener("click", showAndHideInputs);




const applyStyleBtn = document.querySelector("#submit_style_btn");


const styleSizeSelect = document.querySelector("#fontsizeSelect");
const styleFamilySelect = document.querySelector("#fontfamily_select");
const styleWeightSelect = document.querySelector("#textstyle");
const styleColorSelect = document.querySelector("#fontcolor_input");

const customStyleSize = document.querySelector("#custom_size_input");
const customStyleFamily = document.querySelector("#custom_family_input");
const customStyleWeight = document.querySelector("#custom_weight_input");

const applyCustomStyle = (Thetable)=> {
  applyStyleBtn.addEventListener("click", ()=> {

    if (customStyleSize.value != "" && customStyleSize.value > 0) {
      Thetable.style.fontSize = customStyleSize.value + "px";
    } else {
      Thetable.style.fontSize = styleSizeSelect.value + "px";
    }

    if (customStyleFamily.value.trim() != ""){
      Thetable.style.fontFamily = customStyleFamily.value.trim();
    } else {
      Thetable.style.fontFamily = styleFamilySelect.value;
    }

    if (customStyleWeight.value != "" && customStyleWeight.value > 0) {
      Thetable.style.fontWeight = customStyleWeight.value;
    } else {
      Thetable.style.fontWeight = styleWeightSelect.value;
    }


    Thetable.style.color = styleColorSelect.value;
  });
};


/* Helper end */


/* Multi toggler */
let allUpArrows = document.querySelectorAll(".uparrow");
let allDownArrows = document.querySelectorAll(".downarrow");


   allDownArrows[1].click();
   allDownArrows[0].click();


allUpArrows[0].addEventListener("click", ()=> {
   allUpArrows[1].click();

   if (allDownArrows[0].classList.contains("hidden_arrow_style")){
       allDownArrows[0].classList.remove("hidden_arrow_style");
   }
   if (allDownArrows[1].classList.contains("hidden_arrow_style")){
       allDownArrows[1].classList.remove("hidden_arrow_style");
   }

   if (!allUpArrows[0].classList.contains("hidden_arrow_style")){
       allUpArrows[0].classList.add("hidden_arrow_style");
   }
   if (!allUpArrows[1].classList.contains("hidden_arrow_style")){
       allUpArrows[1].classList.add("hidden_arrow_style");
   }

});

allUpArrows[1].addEventListener("click", ()=> {

   allUpArrows[0].click();
   if (allDownArrows[0].classList.contains("hidden_arrow_style")){
       allDownArrows[0].classList.remove("hidden_arrow_style");
   }
   if (allDownArrows[1].classList.contains("hidden_arrow_style")){
       allDownArrows[1].classList.remove("hidden_arrow_style");
   }

   if (!allUpArrows[0].classList.contains("hidden_arrow_style")){
       allUpArrows[0].classList.add("hidden_arrow_style");
   }
   if (!allUpArrows[1].classList.contains("hidden_arrow_style")){
       allUpArrows[1].classList.add("hidden_arrow_style");
   }
});





allDownArrows[0].addEventListener("click", ()=> {
   allDownArrows[1].click();


   if (!allDownArrows[0].classList.contains("hidden_arrow_style")){
       allDownArrows[0].classList.add("hidden_arrow_style");
   }
   if (!allDownArrows[1].classList.contains("hidden_arrow_style")){
       allDownArrows[1].classList.add("hidden_arrow_style");
   }

   if (allUpArrows[0].classList.contains("hidden_arrow_style")){
       allUpArrows[0].classList.remove("hidden_arrow_style");
   }
   if (allUpArrows[1].classList.contains("hidden_arrow_style")){
       allUpArrows[1].classList.remove("hidden_arrow_style");
   }



});

allDownArrows[1].addEventListener("click", ()=> {
   allDownArrows[0].click();
   if (!allDownArrows[0].classList.contains("hidden_arrow_style")){
       allDownArrows[0].classList.add("hidden_arrow_style");
   }
   if (!allDownArrows[1].classList.contains("hidden_arrow_style")){
       allDownArrows[1].classList.add("hidden_arrow_style");
   }

   if (allUpArrows[0].classList.contains("hidden_arrow_style")){
       allUpArrows[0].classList.remove("hidden_arrow_style");
   }
   if (allUpArrows[1].classList.contains("hidden_arrow_style")){
       allUpArrows[1].classList.remove("hidden_arrow_style");
   }


});

/* Multi toggle end */


const upTableArrow = document.getElementById("uptablearrow");

const downTableArrow = document.getElementById("downtableArrow");

upTableArrow.addEventListener("click",()=> {
  if (!upTableArrow.classList.contains("hidden_arrow_style")){
    upTableArrow.classList.add("hidden_arrow_style");
  }
  if (downTableArrow.classList.contains("hidden_arrow_style")){
    downTableArrow.classList.remove("hidden_arrow_style");
  }
});

downTableArrow.addEventListener("click",()=> {
  if (!downTableArrow.classList.contains("hidden_arrow_style")){
    downTableArrow.classList.add("hidden_arrow_style");
  }
  if (upTableArrow.classList.contains("hidden_arrow_style")){
    upTableArrow.classList.remove("hidden_arrow_style");
  }
});


const openStyleEye = document.getElementById("eyeopen_id");
const closeStyleEye = document.getElementById("eyeclose_id");

openStyleEye.click();

openStyleEye.addEventListener("click",()=> {
  if (!openStyleEye.classList.contains("hidden_eye")){
    openStyleEye.classList.add("hidden_eye");
  }
  if (closeStyleEye.classList.contains("hidden_eye")){
    closeStyleEye.classList.remove("hidden_eye");
  }
});

closeStyleEye.addEventListener("click",()=> {
  if (!closeStyleEye.classList.contains("hidden_eye")){
    closeStyleEye.classList.add("hidden_eye");
  }
  if (openStyleEye.classList.contains("hidden_eye")){
    openStyleEye.classList.remove("hidden_eye");
  }
});




/* Request to File and display all sheets within it */
/* displayOptions will create new options for each worksheet for the givin file and display it  */
const displayOptions = (data, message)=> {
  if (data.length > 0){
    const documentFragment = document.createDocumentFragment();

    data.forEach( (option)=> {
      let newOption = document.createElement("option");
      newOption.value = option.id;
      newOption.title = "System path: " + option.path;
      newOption.innerText = `${option.name} (${option.filename})`;
      documentFragment.appendChild(newOption);
    });
    worksheetSelect.appendChild(documentFragment);
    worksheetSelect.options[1].selected = "true"
    return true;
  } else {
    displayErrorMessage(excelSheetsData.message);
    return false;
  }
};

/* Toolbar variables */
const modelCellTitlte = document.getElementById("model_column_title");
const modelCelldimension = document.getElementById("row_dimension");
const modelCellEditValue = document.getElementById("py_editcell");
const modelSubmitEdit = document.getElementById("toolbar_submit_btn");
const modelDeleteRowSubmit = document.getElementById("delete_selected_row");




/* Function to show Edit Menu  */
function createSlideMenu(event) {

  let rowdbId = event.target.getAttribute("data-row-dbid");
  let trRow = document.querySelector(`tr[data-dbid='${rowdbId}']`);
  let cellColumnTitle = event.target.getAttribute("data-column-title");
  let cellRowOrder = event.target.getAttribute("data-row-order");
  let cellOrder = event.target.getAttribute("data-cell-order");
  let cellValue = event.target.getAttribute("data-value");
  let cellDbTable = event.target.getAttribute("data-dbtable");
  let cellId = event.target.getAttribute("id");
  let currentPage = event.target.getAttribute("data-current-page");
  let cellsheetId = event.target.getAttribute("data-sheet-id");
  let dataTotalPages = event.target.getAttribute("data-total");
  let AddToFilterBtn = document.querySelector("#add_to_filter_btn");
  let AddToAndFilterBtn = document.querySelector("#add_to_and_filter_btn");



  emptyTheseInputsList(document.querySelectorAll(".insert_input"));
  if (!trRow) {return false;}
  modelCellTitlte.innerText = cellColumnTitle;
  modelCelldimension.innerText = `[ row:${cellRowOrder} , cell:${cellOrder} ]`;
  modelCellEditValue.value = cellValue;
  modelCellEditValue.setAttribute("row-dbid", rowdbId);
  modelCellEditValue.setAttribute("cell-column-title", cellColumnTitle);
  modelCellEditValue.setAttribute("data-dbtable", cellDbTable);
  modelCellEditValue.setAttribute("data-cell-id", cellId);
  modelCellEditValue.setAttribute("data-current-page", currentPage);
  modelCellEditValue.setAttribute("data-sheet-id", cellsheetId);
  modelCellEditValue.setAttribute("data-total", dataTotalPages);

  AddToFilterBtn.setAttribute("data-column-title", cellColumnTitle);
  AddToFilterBtn.setAttribute("data-cell-value", cellValue);

  AddToAndFilterBtn.setAttribute("data-column-title", cellColumnTitle);
  AddToAndFilterBtn.setAttribute("data-cell-value", cellValue);
  AddToAndFilterBtn.setAttribute("data-row-order", cellRowOrder);




}


/* updateCell Function */
modelSubmitEdit.addEventListener("click", updateCellValue);
async function updateCellValue () {
  const cellValue = modelCellEditValue.value;
  const rowDbId = modelCellEditValue.getAttribute("row-dbid");
  const columnTitle = modelCellEditValue.getAttribute("cell-column-title");
  const cellTableName = modelCellEditValue.getAttribute("data-dbtable");
  const dataCellId = modelCellEditValue.getAttribute("data-cell-id");
  const cellElement = document.querySelector(`#${dataCellId}`);
  /* Client Side Check */
  if (!rowDbId || rowDbId.trim() == "") {return false;}
  if (!columnTitle || columnTitle.trim() == "") {return false;}
  if (!cellTableName || cellTableName.trim() == "") {return false;}
  if (!cellElement) {return false;}
  /* Note the customer maybe need make the value empty */
  const updateRequestData = {id: rowDbId, column: columnTitle, value: cellValue, table: cellTableName};
  const editRes = await sendPostRequest('/update_cell', updateRequestData);
  const result = await editRes.json();
  if (result.code != 200) {/* show error */ return false;}

  let updatedValue = result.value;
  cellElement.innerText = updatedValue;
  cellElement.setAttribute("data-value", updatedValue);
}

async function deleteRowFunction() {
  const rowDbId = modelCellEditValue.getAttribute("row-dbid");
  const rowHTML = document.querySelector(`#row_${rowDbId}`);
  const rowTableName = modelCellEditValue.getAttribute("data-dbtable");

  if (!rowHTML) { return false; }
  if (!rowTableName || rowTableName.trim() == "") {return false;}
  if (!rowDbId || rowDbId.trim() == "") {return false;}
  const deleteRequestData = {id: rowDbId, table: rowTableName};
  const deleteRes = await sendPostRequest('/delete_row', deleteRequestData);
  const deleteResult = await deleteRes.json();

  if (deleteResult.code != 200) {/* show error  */ return false;}
  rowHTML.remove();
  return true;
}
/* Delete Row Function */
modelDeleteRowSubmit.addEventListener("click", deleteRowFunction);

/* Insert row after function */
async function insertRowAfter(event){
  if (event.target.classList.contains("disabled")){return false;}
  if (!event.target.classList.contains("disabled")){event.target.classList.add("disabled");}
  const currentRowid = modelCellEditValue.getAttribute("row-dbid");
  const currentTableName = modelCellEditValue.getAttribute("data-dbtable");
  let currentPage = modelCellEditValue.getAttribute("data-current-page");
  const allInsertInputsValues = document.querySelectorAll("input.insert_input");
  const currentSheetid = modelCellEditValue.getAttribute("data-sheet-id");

  if (currentTitlesList.length == 0){
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!currentRowid || currentRowid.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!currentTableName || currentTableName.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!allInsertInputsValues || allInsertInputsValues.length == 0) {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  const futureRowId =  Number(currentRowid) + 1;
  let cell_values = [];
  /* ID not listed in inputs but listed in titles */
  cell_values.push(futureRowId);
  allInsertInputsValues.forEach( (iInput)=> {
    cell_values.push(iInput.value);
  });
  insertAfterData = {tablename: currentTableName, current_id: currentRowid, column_names: currentTitlesList, values: cell_values};
  const insertAfterRes = await sendPostRequest('/insert_row_after', insertAfterData);
  const insertAfterResult = await insertAfterRes.json();
  if (insertAfterResult.code != 200) {
    /* show error */
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
  if (!currentPage || currentPage.trim() == ""){return false;}
  currentPage = Number(currentPage);
  renderExcelSheet(event, pag=currentPage, recall=currentSheetid);

}
modelInsertAfterInput.addEventListener( "click", insertRowAfter);



/* Insert row before function */
async function insertRowBefore(event){
  if (event.target.classList.contains("disabled")){return false;}
  if (!event.target.classList.contains("disabled")){event.target.classList.add("disabled");}
  const currentRowid = modelCellEditValue.getAttribute("row-dbid");
  const currentTableName = modelCellEditValue.getAttribute("data-dbtable");
  let currentPage = modelCellEditValue.getAttribute("data-current-page");
  const allInsertInputsValues = document.querySelectorAll("input.insert_input");
  const currentSheetid = modelCellEditValue.getAttribute("data-sheet-id");

  if (currentTitlesList.length == 0){
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!currentRowid || currentRowid.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!currentTableName || currentTableName.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!allInsertInputsValues || allInsertInputsValues.length == 0) {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  const futureRowId =  currentRowid;
  let cell_values = [];
  /* ID not listed in inputs but listed in titles */
  cell_values.push(futureRowId);
  allInsertInputsValues.forEach( (iInput)=> {
    cell_values.push(iInput.value);
  });
  insertBeforeData = {tablename: currentTableName, current_id: currentRowid, column_names: currentTitlesList, values: cell_values};
  const insertBeforeRes = await sendPostRequest('/insert_row_before', insertBeforeData);
  const insertBeforeResult = await insertBeforeRes.json();
  if (insertBeforeResult.code != 200) {
    /* show error */
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
  if (!currentPage || currentPage.trim() == ""){return false;}
  currentPage = Number(currentPage);
  renderExcelSheet(event, pag=currentPage, recall=currentSheetid);

}
modelInsertBeforeInput.addEventListener( "click", insertRowBefore);



/* Insert row normal function */
async function insertInto(event){
  if (event.target.classList.contains("disabled")){return false;}
  if (!event.target.classList.contains("disabled")){event.target.classList.add("disabled");}
  let currentTotalPages = modelCellEditValue.getAttribute("data-total");
  const currentTableName = modelCellEditValue.getAttribute("data-dbtable");
  const allInsertInputsValues = document.querySelectorAll("input.insert_input");
  const currentSheetid = modelCellEditValue.getAttribute("data-sheet-id");

  if (!currentTotalPages || currentTotalPages.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }

  if (currentTitlesList.length == 0){
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!currentTableName || currentTableName.trim() == "") {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (!allInsertInputsValues || allInsertInputsValues.length == 0) {
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }

  let columnsWithoutid = [];
  currentTitlesList.forEach( (col, index)=>{
    if (index != 0){
      columnsWithoutid.push(col)
    }
  })
  let cell_values = [];
  /* ID not listed in inputs but listed in titles */
  /* this usless python or ignore value in 0 but if not */
  let lastSaver =  Math.floor((Math.random() * 124555) + 9000);
  cell_values.push(lastSaver)
  allInsertInputsValues.forEach( (iInput)=> {
    cell_values.push(iInput.value);
  });
  insertData = {tablename: currentTableName, column_names: currentTitlesList, values: cell_values};
  const insertBeforeRes = await sendPostRequest('/insert_into', insertData);
  const insertBeforeResult = await insertBeforeRes.json();
  if (insertBeforeResult.code != 200) {
    /* show error */
    if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
    return false;
  }
  if (event.target.classList.contains("disabled")){event.target.classList.remove("disabled");}
  currentTotalPages = Number(currentTotalPages);
  renderExcelSheet(event, pag=currentTotalPages, recall=currentSheetid);

}
modelInsertEndBtn.addEventListener( "click", insertInto);



/* Function will Send A get request that contais file id to get the sheets and call the  displayOptions above */
async function getFileSheets() {

  const fileId = selectFileSelectBox.value;
  worksheetSelect.innerHTML = defaultOptionSelect;

  if (fileId == 'none') { displayErrorMessage("Please select a file");
    return false;
 }
  /* Send A request to get the sheets */
  const res = await fetch(`/getsheets/${fileId}`);
  const excelSheetsData = await res.json();
  if (excelSheetsData.code != 200){
    displayErrorMessage(excelSheetsData.message);
  } else {
    displayOptions(excelSheetsData.data, excelSheetsData.message);
  }
}
selectFileBtn.addEventListener( "click", getFileSheets );
/* display Worksheet options end */


/* Render table Code */
async function renderExcelSheet(event, pag=1, recall=false, order_column='id', order_type='ASC', last_order_id=false) {



 if (worksheetBtn.classList.contains("disabled")) {return false;}

 if (!worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.add("disabled");}

 tableCardContainer.innerHTML = "";
 sheetTableTitle.innerHTML = "";
 let sheet_id = worksheetSelect.value;
 if (recall != false){
    sheet_id = recall;
 }
 sheetTableTitle.setAttribute("data-sheetid", sheet_id);
 if (sheet_id == "none"){
   displayErrorMessage("Please select a sheet");
   if (worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.remove("disabled");}
   return false;
 }
 paginationPerPage = pagenationPerPageInpt.value;
 const sheetResponse = await fetch(`/table_data/${sheet_id}/${pag}/${order_column}/${order_type}?perpage=${paginationPerPage}`);
 const sheetData = await sheetResponse.json();
 if (sheetData.code != 200){
   displayErrorMessage(sheetData.message);
   if (worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.remove("disabled");}
   return false;
 }
 if (worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.remove("disabled");}
 const theStyleCustomizerContainer = document.querySelector("#font_style_container");
 theStyleCustomizerContainer.style.display = "block";



 sheetTableTitle.innerHTML = sheetData.name + " (" + sheetData.total + ")";

 currentTitlesList = sheetData.data.titles;
 // pag
 totalPages = pagRound(sheetData.total/paginationPerPage);
 const inputsFragment = document.createDocumentFragment();


 let tableTemplate = `                                  <div class="table-responsive">
                                                          <div id="csv_table_id" class="dataTables_wrapper dt-bootstrap4 no-footer">
                                                          <div class="row mb-3" id="download_info_row" style="none;">
                                                            <div><span class="pr-2">Last Download Path:</span> <a id="download_link_path" href=""></a></div>
                                                          </div>
                                                             <div class="row mb-4">
                                                                 <div class="d-flex flex-wrap bg-light">
                                                                   <div class="p-2 border mr-3">`


//odrer_type order_by



let firstSelect = '<select class="form-control" id="orderby_selector">';
let titleRowsString  = '';
sheetData.data.titles.forEach( (title, index)=> {
  let checkerifOrdered = last_order_id == `th_${index}` ? "background:lightblue;" : "";
  let checkerifOrderedTitle = last_order_id == `th_${index}` ? `the Last order was ${title} Order Type wast ${order_type}` : "";

  const titlesRow = `<th  title = "${checkerifOrderedTitle}" id="th_${index}" class="sorting_asc title_column_th" data-sheet-id="${sheet_id}" data-toggle="modal" data-target="#title_order_model" data-value="${title}" tabindex="0" aria-controls="csv_main_table" rowspan="1" colspan="1" aria-sort="ascending" aria-label="ID: activate to sort column descending" id="title_${index}" style="width: 107.75px;${checkerifOrdered}">${title}</th>`;
  let selected = (sheetData.order_by == title) ? ' selected' : '';
  firstSelect += `<option value="${title}" ${selected}>${title}</option>`;

  titleRowsString += titlesRow;
  if (index != 0) {
    let newInputContainer = document.createElement("div");
    let newInputElm = document.createElement("input");
    newInputContainer.classList.add("p-2", "border");
    newInputElm.classList.add("form-control", "insert_input");
    newInputElm.setAttribute("placeholder", `Enter ${title}`);
    newInputContainer.appendChild(newInputElm);
    inputsFragment.appendChild(newInputContainer);
  }
});
firstSelect += '</select></div>';
modelInsertInputsHtml.innerHTML = "";
modelInsertInputsHtml.appendChild(inputsFragment);

let ascCheck = (sheetData.odrer_type == "ASC") ? "selected" : "";
let descCheck = (sheetData.odrer_type == "DESC") ? "selected" : "";
tableTemplate += firstSelect;
tableTemplate += `
                                                                 <div class="p-2 mr-3 border">
                                                                  <select class="form-control" id="ordertype_selector">
                                                                     <option value="ASC" ${ascCheck}>Ascending</option>
                                                                     <option value="DESC" ${descCheck}>Descending</option>
                                                                  </select>
                                                                  </div>
                                                                  <div class="p-2 mr-1 border">
                                                                    <button class="btn btn-primary" id="order_submit_btn" title="Apply the Order settings">Apply Changes</button>
                                                                  </div>
                                                                  <div class="p-2 mr-1 border">
                                                                    <button class="btn btn-success" id="download_zip_csv" title="Click here to download the CSV file, note that the folder in Downloads will be downloaded inside the Today folder">Download File</button>
                                                                  </div>
                                                                </div>
                                                            </div>
















                                                            <div class="row">
                                                              <div class="col-auto my-1 col-12">
                                                                <div class="form-row align-items-center">
                                                                  <div class="col-auto my-1 col-8"><input id="apply_filter_inpt"  class="form-control"></div>
                                                                     <div class="col-auto my-1 col-3">
                                                                        <button style="width:100%;" class="btn btn-success" id="apply_filter_btn" title="Click to apply filter">Apply (OR) Filter</button>
                                                                     </div>
                                                                  </div>
                                                                </div>
                                                            </div>

                                                            <div class="row">
                                                              <div class="col-auto my-1 col-12">
                                                                <div class="form-row align-items-center">
                                                                  <div class="col-auto my-1 col-8"><input id="apply_and_filter_inpt"  class="form-control"></div>
                                                                     <div class="col-auto my-1 col-3">
                                                                        <button style="width:100%;" class="btn btn-success" id="apply_and_filter_btn" title="Click to apply filter">Apply (AND) Filter</button>
                                                                     </div>
                                                                  </div>
                                                                </div>
                                                            </div>


                                                            <div class="row">
                                                               <div class="col-sm-12">
                                                                  <table id="csv_main_table" class="table table-bordered table-striped text-center dataTable no-footer" role="grid" aria-describedby="csv_table_info">
                                                                     <thead>
                                                                     <tr role="row">
                                                                         `;
tableTemplate += titleRowsString;
tableTemplate += `</tr></thead>`;

//even
let rowValues = '<tbody>'
sheetData.data.rows.forEach( (row, index)=> {
  let rowClass = (index % 2 == 0) ? 'even' : 'odd';
  rowValues += `<tr style="height:100px;" data-dbid="${row[0]}" id="row_${row[0]}" role="row" class="${rowClass}">`;
      row.forEach( (cell, cellindex)=> {  rowValues += `<td class="sorting_1 cell_class cell_for_sidemenu" data-row-htmlid="row_${row[0]}" data-row-dbid="${row[0]}" data-value="${cell}"  data-row-order="${index}" data-cell-order="${cellindex}" data-dbtable="${sheetData.table}" data-column-title="${sheetData.data.titles[cellindex]}" data-current-page="${pag}" id="cell_${row[0]}_${cellindex}" data-total="${totalPages}"  data-toggle="modal" data-target="#toolbar_model" data-sheet-id="${sheet_id}">${cell}</td>` });
  rowValues += '</tr>';
});

tableTemplate += rowValues + "</tbody>";

let tableTail = `

                                                                   </table>
                                                                </div>
                                                             </div>
                                                             <div class="row">
                                                                <div class="col-sm-12 col-md-7">
                                                                   <div class="dataTables_paginate paging_simple_numbers" id="users_table_paginate">
                                                                      <ul class="pagination">

                                                                      `;
let btnsMax = pagRound(pag/pagBtnsLimit) * pagBtnsLimit;

let btnsMin = (btnsMax - pagBtnsLimit) +1;

let nextPage = btnsMax < totalPages ? btnsMax+1 : btnsMax;
let previousPage = btnsMin > pagBtnsLimit ? btnsMin - 1 : btnsMin;

if (btnsMin > pagBtnsLimit) {
   tableTail += `<li data-sheet-id="${sheet_id}" class="paginate_button page-item previous" data-next-page="${nextPage}" data-btns-min="${btnsMin}"  data-btns-max="${btnsMax}" data-page="${pag}" data-total="${totalPages}" data-previous-page="${previousPage}" id="sheet_table_previous"><a href="#" aria-controls="csv_main_table" data-dt-idx="0" tabindex="0" class="page-link">Previous</a></li>`;
} else {
   tableTail += `<li data-sheet-id="${sheet_id}" class="paginate_button page-item previous disabled" id="sheet_table_previous"><a href="#" aria-controls="csv_main_table" data-dt-idx="${previousPage}" tabindex="0" class="page-link">Previous</a></li>`;
}
for (var i=0; i<totalPages; i++){
  let currentPage = i+1;

  let shownBtnsDisplay = (currentPage >= btnsMin &&  currentPage <= btnsMax) ? 'inline' : 'none';
  if (currentPage==pag){
    tableTail += `<li data-sheet-id="${sheet_id}" data-value="${currentPage}" style="cursor:pointer;" class="paginate_button page-item active paginate_numric_button"><a aria-controls="csv_main_table" data-dt-idx="${currentPage}" tabindex="0" data-sheet-id="${sheet_id}" data-value="${currentPage}" class="page-link pag_button">${currentPage}</a></li>`;
  } else {
    tableTail += `<li data-sheet-id="${sheet_id}" data-value="${currentPage}" style="display:${shownBtnsDisplay};cursor:pointer;" class="paginate_button page-item paginate_numric_button"><a aria-controls="csv_main_table" data-dt-idx="${currentPage}" data-sheet-id="${sheet_id}" data-value="${currentPage}" tabindex="0" class="page-link pag_button">${currentPage}</a></li>`;
  }
};
//(newBtnMax + 1) >= dataTotal
//totalPages/pagBtnsLimit > 1
if (btnsMax + 1 < totalPages) {
  tableTail += `<li data-sheet-id="${sheet_id}" data-btns-max="${btnsMax}" data-page="${pag}" data-total="${totalPages}" data-next-page="${nextPage}" class="paginate_button page-item next" id="sheets_table_next"><a href="#" aria-controls="csv_main_table" data-dt-idx="${nextPage}" tabindex="0" class="page-link">Next</a></li>`;
} else {
  tableTail += `<li data-sheet-id="${sheet_id}" class="paginate_button page-item next disabled" id="sheets_table_next"><a href="#" aria-controls="csv_main_table" data-dt-idx="2" tabindex="0" class="page-link">Next</a></li>`;
}
tableTail += `

                                                                      </ul>
                                                                   </div>
                                                                </div>
                                                             </div>
                                                          </div>
                                                       </div>
                                                       `;
  tableTemplate += tableTail;
  let newCardBody = document.createElement("div");
  newCardBody.classList.add("card-body");
  newCardBody.innerHTML = tableTemplate;
  tableCardContainer.appendChild(newCardBody);



  let allColumnsTitles = document.querySelectorAll(".title_column_th");
  allColumnsTitles.forEach( (elm, click)=>{
    elm.addEventListener("click", openTheOrderModel);
  });

  let theAddedTable = document.querySelector("#csv_main_table");
  applyCustomStyle(theAddedTable);

  /* Function for Single Pag Btn number */
  let allPagenteBtns = document.querySelectorAll("li.paginate_numric_button");
  allPagenteBtns.forEach( (pagBtn)=> {
    pagBtn.addEventListener("click", (event)=> {
      if (event.target.classList.contains("active")) {
        return false;
      }
      let theSheetId = Number(event.target.getAttribute("data-sheet-id"));
      let targetPage = Number(event.target.getAttribute("data-value"));
      renderExcelSheet(event, pag=targetPage, recall=theSheetId);
    });
  });
  const allCells = document.querySelectorAll(".cell_class");
  const allTrs = document.querySelectorAll("#csv_table_id tbody tr");
  const applyFilterBtn = document.querySelector("#apply_filter_btn");
  const applyFilterInput = document.querySelector("#apply_filter_inpt");
  const modelAddToFilterBtn = document.querySelector("#add_to_filter_btn");

  const applyAndFilterBtn = document.querySelector("#apply_and_filter_btn");
  const applyAndFilterInput = document.querySelector("#apply_and_filter_inpt");
  const modelAddToAndFilterBtn = document.querySelector("#add_to_and_filter_btn");

  let filter_string_and = "";
  let addedToFilterList_and = [];


  /* function for  AND filter */
  function filterAndHandler(event){
    let singleFilterTemplate = "";
    /* Handle unuesal and repeated */
    let plainTemplate = `${event.target.getAttribute("data-column-title")}:${event.target.getAttribute("data-cell-value")}:${event.target.getAttribute("data-row-order")}`;
    if (addedToFilterList_and.includes(plainTemplate)){
      return false;
    }


    if (applyAndFilterInput.value.trim().length == 0){
      singleFilterTemplate = plainTemplate;
      addedToFilterList_and.push(plainTemplate);
    } else {
      singleFilterTemplate = ` and ${plainTemplate} `;
      addedToFilterList_and.push(plainTemplate);
    }

    filter_string_and += singleFilterTemplate;
    applyAndFilterInput.value = filter_string_and;

    return true;
  }
  modelAddToAndFilterBtn.addEventListener("click", filterAndHandler);



   /* the submit and filter */
  function submitAndFilter(){
    const allTrs1 = document.querySelectorAll("#csv_table_id tbody tr");
    allTrs1.forEach( (therow)=> {
      if (therow.classList.contains("show_row")){
        therow.classList.remove("show_row");
      }
      if (therow.classList.contains("hide_row")){
        therow.classList.remove("hide_row");
      }
    });


    let andDataList = [];
    addedToFilterList_and.forEach( (condItem)=> {
      let condItemList = condItem.split(':');
      if (condItemList.length == 3){
        andDataList.push( { column: condItemList[0], value: condItemList[1], row: condItemList[2] } );
      }
    });

    /* 2 */
    let projectData = [];

    for (let row=0; row<allTrs1.length; row++) {
      let target_row_list = [];
      andDataList.forEach( (conditionObj)=> {
        let miniTargetTd = allTrs1[row].querySelector(`td[data-column-title='${conditionObj.column}']`);
          target_row_list.push({value: miniTargetTd.innerText, rowid: miniTargetTd.getAttribute("data-row-htmlid"), targetValue: conditionObj.value});

      });
      projectData.push(target_row_list);
    }
    /* now we have the douple array loop and check if value = target 1 point if points = array.length hf and bye bye */
    //console.log(projectData);
    let validRows = [];
    projectData.forEach( (arrayRow, index)=>{
      let equalPoint = 0;
      let arrayLength = arrayRow.length;
      let rowId = '';
      arrayRow.forEach( (tdObj)=>{
        if (tdObj.value == tdObj.targetValue){
          equalPoint += 1;
          rowId = tdObj.rowid;
        }
      });

      if (equalPoint == arrayLength){
        validRows.push(rowId);
      }
    });
    /* hide and show step */
    allTrs1.forEach( (trRow)=>{
      let trId = trRow.getAttribute("id");
      if (validRows.includes(trId)){
        if (!trRow.classList.contains("show_row")){
          trRow.classList.add("show_row");
        }
      } else {
        if (!trRow.classList.contains("hide_row")){
          trRow.classList.add("hide_row");
        }
      }
    });

  }
  applyAndFilterBtn.addEventListener("click", submitAndFilter);

  /* function to return the rows if filter empty */
  applyAndFilterInput.addEventListener("keyup", backRowsDefault);

  function backRowsDefaultAnd() {
    const allTrs1 = document.querySelectorAll("#csv_table_id tbody tr");
    const filterInptValue = applyAndFilterInput.value;
    const filterInptValueOr = applyFilterInput.value;

    allTrs1.forEach( (therow)=> {
      if (therow.classList.contains("show_row")){
        therow.classList.remove("show_row");
      }
      if (therow.classList.contains("hide_row")){
        therow.classList.remove("hide_row");
      }
    });
    // back filter string and list empty
    filter_string_and = "";
    addedToFilterList_and = [];
    return true;
  }


  /* END OF ADD FILTER  */
  /* function for filter */




  /* The Real Filter function  */
  function filterHandler(event){
    let singleFilterTemplate = "";
    /* Handle unuesal and repeated */
    let plainTemplate = `${event.target.getAttribute("data-column-title")}:${event.target.getAttribute("data-cell-value")}`;
    if (addedToFilterList.includes(plainTemplate)){
      return false;
    }
    /*
    if (applyFilterInput.value.trim() == ""){
      filter_string = "";
      addedToFilterList = [];
    }*/

    if (applyFilterInput.value.trim().length == 0){
      singleFilterTemplate = plainTemplate;
      addedToFilterList.push(plainTemplate);
    } else {
      singleFilterTemplate = ` or ${plainTemplate} `;
      addedToFilterList.push(plainTemplate);
    }

    filter_string += singleFilterTemplate;
    applyFilterInput.value = filter_string;



    return true;

  }
  modelAddToFilterBtn.addEventListener("click", filterHandler);

  /* function to return the rows if filter empty */
  applyFilterInput.addEventListener("keyup", backRowsDefault);

  function backRowsDefault() {
    const allTrs2 = document.querySelectorAll("#csv_table_id tbody tr");
    const filterInptValue = applyFilterInput.value;
    if (!filterInptValue || filterInptValue.trim() == "" ) {
      allTrs2.forEach( (therow)=> {
        if (therow.classList.contains("show_row")){
          therow.classList.remove("show_row");
        }
        if (therow.classList.contains("hide_row")){
          therow.classList.remove("hide_row");
        }
      });
      // back filter string and list empty
      filter_string = "";
      addedToFilterList = [];
      return true;
    }
  }






  function submitFilter(){
    const allTrs2 = document.querySelectorAll("#csv_table_id tbody tr");
    const filterInptValue = applyFilterInput.value;
    if (!filterInptValue || filterInptValue.trim() == "" ) {
      allTrs2.forEach( (therow)=> {
           if (therow.classList.contains("show_row")){
             therow.classList.remove("show_row");
           }
           if (therow.classList.contains("hide_row")){
             therow.classList.remove("hide_row");
           }
      });
      filter_string = "";
      addedToFilterList = [];
      return false;
    }

    allTrs2.forEach( (therow)=> {
         if (therow.classList.contains("show_row")){
           therow.classList.remove("show_row");
         }
         if (therow.classList.contains("hide_row")){
           therow.classList.remove("hide_row");
         }
    });

    for (let i=0; i<addedToFilterList.length; i++){
      let tagList = addedToFilterList[i].split(":");
      if (tagList.length < 2) {
        continue;
      }
      let tagColumnName = tagList[0];
      let tagValue = tagList[1];

      console.log(tagList);
      // get all column value with same name
      const thisColumn = document.querySelectorAll(`[data-column-title=${tagColumnName}]`);

      thisColumn.forEach( (celInColumn)=> {
        let tryElm = document.querySelector(`#${celInColumn.getAttribute("data-row-htmlid")}`);
        if (celInColumn.innerText.trim() == tagValue.trim()) {
          if (tryElm) {
            //tryElm.style.display = "table-row";
            if (!tryElm.classList.contains("show_row")){
            tryElm.classList.add("show_row");
            }
            // it covered by two ways not add multi and even if multi show has important style
            if (tryElm.classList.contains("hide_row")){
              tryElm.classList.remove("hide_row");
            }

          }
        } else {
          if (tryElm) {
          if (!tryElm.classList.contains("show_row")){
            tryElm.classList.add("hide_row");
          }
        }
      }
    });

    }


  }
applyFilterBtn.addEventListener("click", submitFilter);





  /* add event listener for create cell sidemenu */
  let allTableCells = document.querySelectorAll(".cell_for_sidemenu");
  allTableCells.forEach( (tCell)=> {
    /* Event Listener for hover */
    tCell.addEventListener("click", createSlideMenu);
  });


  /* Second Order Function */
  const theTitlesModelTitle = document.querySelector("#title_order_model h4.modal-title");
  const theTitlesModelSubmit = document.querySelector("#title_order_model #submit_order_titles");
  const theTitlesModelSelect = document.querySelector("#title_order_model #orderby_titles");

  function oktestlast(event) {
    let columnValue = event.target.getAttribute("data-order-by");
    let tableSheetid =  event.target.getAttribute("data-sheet-id");
    let orderedTH =  event.target.getAttribute("data-th-id");

    let lastSelectedTh = document.querySelector(`#${orderedTH}`);
    lastSelectedTh.style.background = "lightblue";
    lastSelectedTh.title = "the table was ordred By " + columnValue + " " + theTitlesModelSelect.value;
    renderExcelSheet(event, pag=pag, recall=tableSheetid, order_column=columnValue, order_type=theTitlesModelSelect.value, orderedTH);
  }

  function openTheOrderModel(event){
    let columnValue = event.target.getAttribute("data-value");
    let tableSheetid =  event.target.getAttribute("data-sheet-id");
    let thId =  event.target.getAttribute("id");

    theTitlesModelTitle.innerText = columnValue;

    theTitlesModelSubmit.setAttribute("data-sheet-id", tableSheetid);
    theTitlesModelSubmit.setAttribute("data-order-by", columnValue);
    theTitlesModelSubmit.setAttribute("data-th-id", thId);

    theTitlesModelSubmit.addEventListener("click", oktestlast);
  }


  /* Function for order */
  function orderBrider(){
    const orderColumnSelector = document.querySelector("#orderby_selector");
    const orderTypeSelector = document.querySelector("#ordertype_selector");
    const orderSheetId = sheetTableTitle.getAttribute("data-sheetid");
    if (!orderTypeSelector || !orderColumnSelector || orderSheetId.trim() == "") {return false;}

    renderExcelSheet(event, pag=pag, recall=orderSheetId, order_column=orderColumnSelector.value, order_type=orderTypeSelector.value);

  }
  let applyOrderBtn = document.getElementById("order_submit_btn");
  applyOrderBtn.addEventListener("click", orderBrider);


  const downloadInfoRow = document.getElementById("download_info_row");
  const downloadInfoLink = document.getElementById("download_link_path");
  const downloadZipBtn = document.getElementById("download_zip_csv");
  hideDownloadInfo(downloadInfoRow, downloadInfoLink);

  /* Function for Download ZIPed CSV */
  async function downloadFileNow(){
    const orderColumnSelector = document.querySelector("#orderby_selector");
    const orderTypeSelector = document.querySelector("#ordertype_selector");
    const orderSheetId = sheetTableTitle.getAttribute("data-sheetid");
    if (!orderTypeSelector || !orderColumnSelector || orderSheetId.trim() == "") {return false;}
    let downloadURL = `/download_csv/${orderSheetId}/${orderColumnSelector.value}/${orderTypeSelector.value}`;
    const downloadRes = await fetch(downloadURL);
    const downloadResult = await downloadRes.json();
    if (downloadResult.code != 200) {return false;}
    showDownloadInfo(downloadInfoRow, downloadInfoLink, downloadResult.path);
  }
  downloadZipBtn.addEventListener("click", downloadFileNow);


  /* Function for next*/
  let nextPagenationGroupBtn = document.querySelector("#sheets_table_next");
  let PreviousGroupBtn = document.querySelector("#sheet_table_previous");
  nextPagenationGroupBtn.addEventListener("click", (event)=> {
    let dataNextPage = Number(nextPagenationGroupBtn.getAttribute("data-next-page"));
    let dataPage = Number(nextPagenationGroupBtn.getAttribute("data-page"));
    let dataTotal = Number(nextPagenationGroupBtn.getAttribute("data-total"));
    let dataBtnMax = Number(nextPagenationGroupBtn.getAttribute("data-btns-max"));
    let dataSheetId = Number(nextPagenationGroupBtn.getAttribute("data-sheet-id"));

    let dataBtnMin = (dataBtnMax - pagBtnsLimit) + 1;
    let allNumbricBtns = document.querySelectorAll(".paginate_numric_button");
    if (dataNextPage<dataTotal){
      let newBtnMax = dataBtnMax + pagBtnsLimit;
      let newBtnMin = (newBtnMax - pagBtnsLimit) + 1;
      let newNextPage = pagBtnsLimit + dataNextPage;

      nextPagenationGroupBtn.setAttribute("data-next-page", newNextPage);
      nextPagenationGroupBtn.setAttribute("data-btns-max", newBtnMax);

      PreviousGroupBtn.setAttribute("data-previous-page", newBtnMin-1);
      PreviousGroupBtn.setAttribute("data-btns-max", newBtnMax);
      PreviousGroupBtn.setAttribute("data-btns-min", newBtnMin);
      PreviousGroupBtn.setAttribute("data-next-page", newNextPage);


      if (PreviousGroupBtn.classList.contains("disabled")){
         PreviousGroupBtn.classList.remove("disabled");
      }

      if ((newBtnMax + 1) >= dataTotal) {

        if (!nextPagenationGroupBtn.classList.contains("disabled")){
           nextPagenationGroupBtn.classList.add("disabled");
        }
      }

      allNumbricBtns.forEach( (numBtn, index)=> {
        let currentIndex = index + 1;
        if (dataNextPage == currentIndex) {
          if (!numBtn.classList.contains("active")){
            numBtn.classList.add("active");
          }
        }
        if (currentIndex >= newBtnMin && currentIndex <= newBtnMax){
          numBtn.style.display = "block";
        } else {
          numBtn.style.display = "none";
        }

      });
      renderExcelSheet(event, pag=dataNextPage, recall=dataSheetId);
    } else {
      if (!nextPagenationGroupBtn.classList.contains("disabled")){
         nextPagenationGroupBtn.classList.add("disabled");
      }
      if (worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.remove("disabled");}
      return false;
    }
  });



    /* Function for previous */

    PreviousGroupBtn.addEventListener("click", (event)=> {
    let dataPreviousPage = Number(PreviousGroupBtn.getAttribute("data-previous-page"));
    let dataNextPage = Number(PreviousGroupBtn.getAttribute("data-next-page"));
    let dataPage = Number(PreviousGroupBtn.getAttribute("data-page"));
    let dataTotal = Number(PreviousGroupBtn.getAttribute("data-total"));
    let dataBtnMax = Number(PreviousGroupBtn.getAttribute("data-btns-max"));
    let dataBtnMin = Number(PreviousGroupBtn.getAttribute("data-btns-min"));
    let pDataSheetId = Number(PreviousGroupBtn.getAttribute("data-sheet-id"));

    //let dataBtnMin = (dataBtnMax - pagBtnsLimit) + 1;
    let allNumbricBtns = document.querySelectorAll(".paginate_numric_button");

    if (dataPreviousPage>=pagBtnsLimit){

      let newBtnMax = dataBtnMax - pagBtnsLimit;
      let newBtnMin = (newBtnMax - pagBtnsLimit) + 1;
      let newNextPage = dataNextPage - pagBtnsLimit;
      let newPerviousPage = dataPreviousPage - pagBtnsLimit;


      nextPagenationGroupBtn.setAttribute("data-next-page", newNextPage);
      nextPagenationGroupBtn.setAttribute("data-btns-max", newBtnMax);

      PreviousGroupBtn.setAttribute("data-previous-page", newPerviousPage);
      PreviousGroupBtn.setAttribute("data-btns-max", newBtnMax);
      PreviousGroupBtn.setAttribute("data-btns-min", newBtnMin);
      PreviousGroupBtn.setAttribute("data-next-page", newNextPage);



      if (nextPagenationGroupBtn.classList.contains("disabled")){
         nextPagenationGroupBtn.classList.remove("disabled");
      }

      if (newPerviousPage == 0) {
        if (!PreviousGroupBtn.classList.contains("disabled")){
           PreviousGroupBtn.classList.add("disabled");
        }
      }


      allNumbricBtns.forEach( (numBtn, index)=> {
        let currentIndex = index + 1;
        if (newBtnMax == currentIndex) {
          if (!numBtn.classList.contains("active")){
            numBtn.classList.add("active");
          }
        } else {
          if (numBtn.classList.contains("active")){
            numBtn.classList.remove("active");
          }
        }

        if (currentIndex >= newBtnMin && currentIndex <= newBtnMax){
          numBtn.style.display = "block";
        } else {
          numBtn.style.display = "none";
        }

      });

      renderExcelSheet(event, pag=dataPreviousPage, recall=pDataSheetId)
    } else {

      if (!PreviousGroupBtn.classList.contains("disabled")){
         PreviousGroupBtn.classList.add("disabled");
      }
      if (worksheetBtn.classList.contains("disabled")) {worksheetBtn.classList.remove("disabled");}
      return false;
    }
  });


}
worksheetBtn.addEventListener( "click", renderExcelSheet);
