<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Reminders.aspx.cs" Inherits="HealthBuddyWebApp.Reminders" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder_head" runat="server">
    <style type ="text/css">
        .gridview 
        {
        width: 100%;
        }
         .gridview tr td{
             text-align:center;
             font-size: small;
         }
        .gridview tr.even td {
            background-color: #efdec6;
        }
        .gridview th 
        {
        color: #000000;
        background-color : #f7b14f;
        padding: 5px;
        font-size:1em;
        font-weight:bold;
        text-align:center;
        }
    </style>
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_roundingOnly" runat="server">
</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
    <h3>Patients yet to complete their Roundings</h3>
    <p>Please Remind Them</p>
        <asp:GridView ID="gv_reminders" runat="server" AlternatingRowStyle-CssClass="even" DataKeyNames="Patient ID"  CssClass="gridview">
<AlternatingRowStyle CssClass="even"></AlternatingRowStyle>
    </asp:GridView>
    </div>
</asp:Content>
