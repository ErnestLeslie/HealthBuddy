<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Patients.aspx.cs" Inherits="HealthBuddyWebApp.Patients" %>

<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_head" runat="server">
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

<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
        <h3>Patients</h3>
        View: <br />
        <asp:LinkButton ID="lb_All" runat="server" OnClick="lb_All_Click">All Patients</asp:LinkButton> | <asp:LinkButton ID="lb_Active" runat="server" OnClick="lb_Active_Click">Active Patients</asp:LinkButton>
        <asp:LinkButton ID="lb_Add" runat="server" CssClass="pull-right" BackColor="#C5EED8" ForeColor="#988C95" OnClick="lb_Add_Click">&nbsp;&nbsp; Add Patient &nbsp;&nbsp; </asp:LinkButton>
        <p><br /></p>
        <asp:Panel ID="pnl_AllPatients" runat="server" Visible = "false">
        <div class="col-md-3 col-sm-4 col-xs-6 pull-right">
            <asp:DropDownList ID="ddl_Sort" runat="server" CssClass="form-control pull-right row b-none"  AutoPostBack="true" OnSelectedIndexChanged="ddl_Sort_SelectedIndexChanged" >
                <asp:ListItem Value="Patient ID ASC">Patient ID (Ascending)</asp:ListItem>
                <asp:ListItem Value="Patient Name ASC">Name (A-Z)</asp:ListItem>
                <asp:ListItem Value="Ward Number ASC">Ward No (Ascending)</asp:ListItem>
                <asp:ListItem Value="Bed Number ASC">Bed No (Ascending)</asp:ListItem>
            </asp:DropDownList>
        </div>
        <br /><br />
        <div>
        <asp:GridView ID="gv_Patients" runat="server"  AlternatingRowStyle-CssClass="even" DataKeyNames="Patient ID"  CssClass="gridview" OnRowCancelingEdit="gv_Patients_RowCancelingEdit" OnRowEditing="gv_Patients_RowEditing" OnRowUpdating="gv_Patients_RowUpdating" OnRowDeleting="gv_Patients_RowDeleting" OnSelectedIndexChanged="gv_Patients_SelectedIndexChanged" OnRowDataBound="gv_Patients_RowDataBound">
            <AlternatingRowStyle CssClass="even"></AlternatingRowStyle>
            <Columns>
                <asp:TemplateField ShowHeader="False">
                    <EditItemTemplate>
                        <asp:LinkButton ID="lb_Update2" runat="server" CausesValidation="True" CommandName="Update" Text="Update"></asp:LinkButton>
                        &nbsp;<asp:LinkButton ID="lb_UpdateCancel" runat="server" CausesValidation="False" CommandName="Cancel" Text="Cancel"></asp:LinkButton>
                    </EditItemTemplate>
                    <ItemTemplate>
                        <asp:LinkButton ID="lb_View" runat="server" CausesValidation="False" CommandName="Select" Text="View Roundings"></asp:LinkButton> |
                        <asp:LinkButton ID="lb_Update" runat="server" CausesValidation="False" CommandName="Edit" Text="Edit"></asp:LinkButton> | 
                        <asp:LinkButton ID="lb_Delete" runat="server" CausesValidation="False" CommandName="Delete" Text="Delete"  OnClientClick="return confirm('Are you sure you want to delete this patient?')"></asp:LinkButton>
                    </ItemTemplate>
                </asp:TemplateField>
            </Columns>
        </asp:GridView>
        <br />
        <asp:Label ID="lbl_Error" runat="server" ForeColor="#d61145" Text="Update Failed: <br/> " Font-Size="Small" Visible="false"></asp:Label>
        </div>
        </asp:Panel>

    </div>
</asp:Content>
