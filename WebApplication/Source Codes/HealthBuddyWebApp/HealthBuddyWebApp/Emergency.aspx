<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Emergency.aspx.cs" Inherits="HealthBuddyWebApp.Emergency" %>
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
        <h3>Emergency</h3>
        <p></p>
        <asp:GridView ID="gv_Emergency" runat="server" AlternatingRowStyle-CssClass="even"  CssClass="gridview" OnRowDeleting="gv_Emergency_RowDeleting">
            <AlternatingRowStyle CssClass="even"></AlternatingRowStyle>
            <Columns>
                <asp:CommandField DeleteText="Attended" ShowDeleteButton="True" />
            </Columns>
        </asp:GridView>
           <asp:Label ID="Label1" runat="server" ForeColor="DarkGreen"></asp:Label>
    </div>
</asp:Content>
