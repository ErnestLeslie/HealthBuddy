<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Devices.aspx.cs" Inherits="HealthBuddyWebApp.Devices" %>
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
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
    <h3>Devices</h3>
    Device Settings can ONLY be changed via the HealthBuddy Alexa Skill.
    <br />
    <p></p>
    <asp:GridView ID="gv_Devices" runat="server" AlternatingRowStyle-CssClass="even"  CssClass="gridview">
        <AlternatingRowStyle CssClass="even"></AlternatingRowStyle>
    </asp:GridView>
    </div>
</asp:Content>
