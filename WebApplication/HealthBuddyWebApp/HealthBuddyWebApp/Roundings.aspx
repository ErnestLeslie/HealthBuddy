<%@ Page Title="" Language="C#" MasterPageFile="~/main.Master" AutoEventWireup="true" CodeBehind="Roundings.aspx.cs" Inherits="HealthBuddyWebApp.Rounding" %>
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
<asp:Content ID="Content3" ContentPlaceHolderID="ContentPlaceHolder_roundingOnly" runat="server">
    <div class="row">
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">Total Roundings</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-success"></i> <span class="counter text-success">
                        <asp:Label ID="lbl_roundingCount" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">Up-to-Date Roundings</h3>
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
                <h3 class="box-title">Outdated Roundings</h3>
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
                <h3 class="box-title">Lastest Rounding</h3>
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
                <h3 class="box-title">Average Glasses of Water</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash5"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-info"></i> <span class="counter text-info">
                        <asp:Label ID="lbl_Avg_Glasses" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
        <div class="col-lg-4 col-sm-6 col-xs-12">
            <div class="white-box analytics-info">
                <h3 class="box-title">Average Visits to Washroom</h3>
                <ul class="list-inline two-part">
                    <li>
                        <div id="sparklinedash6"></div>
                    </li>
                    <li class="text-right"><i class="ti-arrow-up text-warning"></i> <span class="counter text-warning">
                        <asp:Label ID="lbl_Avg_Washroom" runat="server" Text="Error"></asp:Label></span></li>
                </ul>
            </div>
        </div>
     </div>
</asp:Content>

<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder_body" runat="server">
    <div>
        <h3>Roundings</h3>
        View: <br />
        <asp:LinkButton ID="lb_All" runat="server" OnClick="lb_All_Click">All Roundings</asp:LinkButton> | <asp:LinkButton ID="lb_Active" runat="server" OnClick="lb_Active_Click">Up-to-date Roundings</asp:LinkButton> | <asp:LinkButton ID="lb_Outdated" runat="server" OnClick="lb_Outdated_Click">Outdated Roundings</asp:LinkButton> | <asp:LinkButton ID="lb_ByPatient" runat="server" OnClick="lb_ByPatient_Click">By Patient</asp:LinkButton> 
        <p></p>
        <asp:Panel ID="pnl" runat="server" Visible="false">
        Select <a runat="server" href="../Patients.aspx">Patient ID</a>: <asp:DropDownList ID="ddl_Patients" runat="server" AutoPostBack="true" OnSelectedIndexChanged="ddl_Patients_SelectedIndexChanged">
            </asp:DropDownList>
        <p></p>
        </asp:Panel>
        <asp:GridView ID="gv_Roundings" runat="server" AlternatingRowStyle-CssClass="even" DataKeyNames="Rounding ID"  CssClass="gridview" EmptyDataText="No Rounding Records" ></asp:GridView>
    </div>
</asp:Content>
