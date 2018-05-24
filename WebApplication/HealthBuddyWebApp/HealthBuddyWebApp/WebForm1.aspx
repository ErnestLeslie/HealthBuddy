<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="WebForm1.aspx.cs" Inherits="HealthBuddyWebApp.WebForm1" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>Patients</title>
    <style type ="text/css">
        .gridview 
        {
        width: 100%;
        }
         .gridview tr td{
             font-weight:bold;
             text-align:center;
         }
        .gridview tr.even td {
            background-color: #b7b7b7;
            font-weight:bold;
        }
        .gridview th 
        {
        border-bottom: 2px solid #7E1FBD;
        border-top: 2px solid #7E1FBD;
        padding: 5px;
        font-size:1em;
        font-weight:bold;
        }
    </style>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        <h1>HEALTHBUDDY WEB APP (GIMME DISTINCTION)</h1>
        <p>Integrated with Amazon.com and Amazon Web Services<br />
        Created by: Ernest Arbuthnot-Leslie Y.</p>
        <br />
        <b>Sort By:</b> <asp:DropDownList ID="DropDownList1" runat="server" AutoPostBack="true" OnSelectedIndexChanged="DropDownList1_SelectedIndexChanged">
                <asp:ListItem Value="Patient ID ASC">Patient ID (Ascending)</asp:ListItem>
                <asp:ListItem Value="Patient Name ASC">Name (A-Z)</asp:ListItem>
                <asp:ListItem Value="Ward Number ASC">Ward No (Ascending)</asp:ListItem>
                <asp:ListItem Value="Bed Number ASC">Bed No (Ascending)</asp:ListItem>
            </asp:DropDownList>
        <br />
        <br />
        <asp:GridView ID="GridView1" runat="server" AlternatingRowStyle-CssClass="even" CssClass="gridview" DataKeyNames="Patient ID" OnSelectedIndexChanged="GridView1_SelectedIndexChanged" OnRowCancelingEdit="GridView1_RowCancelingEdit" OnRowEditing="GridView1_RowEditing" OnRowUpdating="GridView1_RowUpdating">
            <AlternatingRowStyle CssClass="even"></AlternatingRowStyle>
            <Columns>
                <asp:CommandField ShowEditButton="True" />
            </Columns>
        </asp:GridView>
        <asp:Label ID ="label1" runat="server" Text="Hello"></asp:Label>
    </div>
    </form>
</body>
</html>
