<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Diet.aspx.cs" Inherits="HealthBuddyWebApp.Diet" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder_head" runat="server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_roundingOnly" runat="server">
     <div class="col-lg-4 col-sm-6 col-xs-12">
         <a href="../Diet2.aspx">
            <div class="white-box analytics-info">
                <h3 class="box-title">WESTERN</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-success"></i> <span class="counter text-success">
                        <asp:Label ID="lbl_roundingCount" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
             </a>
        </div>
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">CHINESE</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash2"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-dark"></i> <span class="counter text-dark">
                        <asp:Label ID="lbl_ActiveRoundingCount" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">MUSLIM</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash3"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-danger"></i> <span class="counter text-danger">
                        <asp:Label ID="lbl_OutdatedRoundingCount" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">VEGETARIAN</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash4"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-purple"></i> <span class="counter text-purple">
                        <asp:Label ID="lbl_LastestRounding" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
    <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">Patients Not Selected</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash4"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-warning"></i> <span class="counter text-warning">
                        <asp:Label ID="lbl_unselected" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
    <asp:ListView ID="lv_Address" runat="server" GroupPlaceholderID="groupPlaceholder" OnItemUpdating="lv_Address_ItemUpdating" ItemPlaceholderID="itemPlaceholder" OnItemCanceling="lv_Address_ItemCanceling" OnItemEditing="lv_Address_ItemEditing">
        <LayoutTemplate>
            <table id="tbl_Address">
                    <tr ID="groupPlaceholder" runat="server">
                    </tr>
            </table>
        </LayoutTemplate>
        <GroupTemplate>
                    <tr>
                        <td ID="itemPlaceholder" runat="server">
                        </td>
                    </tr>
         </GroupTemplate>
        <ItemTemplate>
            <td id="add_details"> 
                <b>
                    <asp:Label ID="Label4" runat="server" Font-Bold="true" Font-Size="1.5em" Text="Today's Menu"></asp:Label></b><asp:LinkButton ID="btn_EditAddress" runat="server" CssClass="pull-right" BackColor="#C5EED8" ForeColor="#988C95" CommandName="Edit">&nbsp; Edit &nbsp;</asp:LinkButton><br />
                <asp:Label ID="Label5" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Western: "/><br />
                <asp:Label ID ="lbl_Id" runat="server" Text='<%# Eval("Western") %>' Visible="true" /><br />
                <asp:Label ID="Label6" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Chinese: "/><br />
                <asp:Label ID ="Label1" runat="server" Text='<%# Eval("Chinese") %>' Visible="true" /><br />
                <asp:Label ID="Label7" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Muslim: "/><br />
                <asp:Label ID ="Label2" runat="server" Text='<%# Eval("Muslim") %>' Visible="true" /><br />
                <asp:Label ID="Label8" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Vegetarian: "/><br />
                <asp:Label ID ="Label3" runat="server" Text='<%# Eval("Vegetarian") %>' Visible="true" /><br />
            </td>               
        </ItemTemplate>
        <EditItemTemplate>
            <td id="add_details"> 
                <b><asp:Label ID="Label4" runat="server" Font-Bold="true" Font-Size="1.5em" Text="Today's Menu"></asp:Label></b><asp:LinkButton ID="btn_EditAddress" runat="server" CssClass="pull-right" BackColor="#C5EED8" ForeColor="#988C95" CommandName="Edit">Edit</asp:LinkButton><br />
                <asp:Label ID="Label5" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Western: "/><br />
                <asp:TextBox ID ="tb_Western" runat="server" Text='<%# Bind("Western") %>' Visible="true" /><br />
                <asp:Label ID="Label6" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Chinese: "/><br />
                <asp:TextBox ID ="tb_Chinese" runat="server" Text='<%# Bind("Chinese") %>' Visible="true" /><br />
                <asp:Label ID="Label7" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Muslim: "/><br />
                <asp:TextBox ID ="tb_Muslim" runat="server" Text='<%# Bind("Muslim") %>' Visible="true" /><br />
                <asp:Label ID="Label8" runat="server" Font-Bold="true" Font-Size="1.1em" Text="Vegetarian: "/><br />
                <asp:TextBox ID ="tb_Veg" runat="server" Text='<%# Bind("Vegetarian") %>' Visible="true" /><br />
                    <asp:LinkButton ID="btn_Update" runat="server" style="text-decoration:none;" CommandName="Update">Update</asp:LinkButton> |
                    <asp:LinkButton ID="btn_Cancel" runat="server" style="text-decoration:none;" CommandName="Cancel" CausesValidation="false" >Cancel</asp:LinkButton>
                <br /><asp:Label ID="lbl_Error" runat="server" ForeColor="DarkRed"></asp:Label>
            </td>
        </EditItemTemplate>
    </asp:ListView>
                <asp:Label ID="lbl_12334" runat="server" ForeColor="DarkGreen"></asp:Label>
    <p></p>
       
    </div>
</asp:Content>
