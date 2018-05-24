<%@ Page Title="" Language="C#"  EnableEventValidation="false" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="AddPatient.aspx.cs" Inherits="HealthBuddyWebApp.AddPatient" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder_head" runat="server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_roundingOnly" runat="server">
</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
        <h3>Add Patient</h3>
        <form>
        <table style="width:100%">
            <tr>
                <td>Patient ID: </td>
                <td><asp:label ID="lbl_ID" runat="server" text="Label"></asp:label></td>
            </tr>
            <tr>
                <td>Patient Name:</td>
                <td><asp:textbox ID ="tb_name" runat="server"></asp:textbox></td>
            </tr>
            <tr>
                <td>Patient Phone:</td>
                <td><asp:textbox ID ="tb_phone" runat="server" onkeydown = "return (!((event.keyCode>=65 && event.keyCode <= 95) || event.keyCode >= 106) && event.keyCode!=32);" MaxLength="8"></asp:textbox></td>
            </tr>
            <tr>
                <td>Patient Language:</td>
                <td><asp:dropdownlist ID="ddl_Language" runat="server">
                    <asp:ListItem Value="English">English</asp:ListItem>
                    <asp:ListItem Value="Mandarin">Mandarin</asp:ListItem>
                    </asp:dropdownlist></td>
            </tr>
            <tr>
                <td>Ward No:</td>
                <td><asp:textbox ID ="tb_Ward" runat="server" onkeydown = "return (!((event.keyCode>=65 && event.keyCode <= 95) || event.keyCode >= 106) && event.keyCode!=32);"></asp:textbox></td>
            </tr>
            <tr>
                <td><asp:label ID="lbl_BedNo" runat="server" text="Bed No:" Visible ="true" ></asp:label></td>
                <td><asp:textbox ID ="tb_Bed" runat="server" onkeydown = "return (!((event.keyCode>=65 && event.keyCode <= 95) || event.keyCode >= 106) && event.keyCode!=32);" ></asp:textbox></td>
            </tr>
        </table>
        <br />
        <asp:Label ID="lbl_warning" ForeColor="Red" runat="server"/>
        <table style="width:100%">
            <tr>
                <td><asp:button runat="server" text=" &nbsp;Back&nbsp;" OnClick="Unnamed1_Click" /></td>
                <td style="text-align:right"><asp:button runat="server" text="&nbsp;Save&nbsp;" OnClick="Unnamed2_Click" /></td>
            </tr>
        </table>
        </form>
    </div>
</asp:Content>
