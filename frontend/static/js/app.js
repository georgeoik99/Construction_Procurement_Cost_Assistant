const projectFilter =
    document.getElementById("project-filter");

const categoryFilter =
    document.getElementById("category-filter");

const riskFilter =
    document.getElementById("risk-filter");


const applyFiltersButton =
    document.getElementById("apply-filters");

const refreshButton =
    document.getElementById("refresh-button");


const assistantForm =
    document.getElementById("assistant-form");

const assistantInput =
    document.getElementById("assistant-input");

const chatMessages =
    document.getElementById("chat-messages");


const suggestionToggle =
    document.getElementById("suggestion-toggle");

const suggestionMenu =
    document.getElementById("suggestion-menu");


const navItems =
    document.querySelectorAll(".nav-item");

const tableTabs =
    document.querySelectorAll(".table-tab");

const tablePanels =
    document.querySelectorAll(".table-panel");


const plotConfig = {
    responsive: true,
    displaylogo: false
};


function basePlotLayout() {

    return {
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",

        font: {
            color: "#8f9bad",
            family: "Segoe UI, Arial, sans-serif",
            size: 11
        },

        margin: {
            l: 60,
            r: 20,
            t: 20,
            b: 50
        },

        xaxis: {
            gridcolor: "rgba(148, 163, 184, 0.08)",
            zerolinecolor: "rgba(148, 163, 184, 0.12)",
            automargin: true
        },

        yaxis: {
            gridcolor: "rgba(148, 163, 184, 0.08)",
            zerolinecolor: "rgba(148, 163, 184, 0.12)",
            automargin: true
        }
    };

}


function formatCurrency(value) {

    const numericValue =
        Number(value || 0);


    if (Math.abs(numericValue) >= 1_000_000) {

        return (
            `€${(
                numericValue / 1_000_000
            ).toFixed(1)}M`
        );

    }


    if (Math.abs(numericValue) >= 1_000) {

        return (
            `€${(
                numericValue / 1_000
            ).toFixed(1)}K`
        );

    }


    return (
        `€${numericValue.toLocaleString()}`
    );

}


function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function humanizeColumnName(columnName) {

    return columnName
        .replaceAll("_", " ");

}


function formatDate(value) {

    if (!value) {
        return "";
    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {
        return escapeHtml(value);
    }


    return date.toLocaleDateString();

}


function formatTableCell(
    key,
    value
) {

    const currencyFields = [
        "Total_Cost",
        "Budgeted_Cost",
        "Cost_Variance",
        "Unit_Cost",
        "Avg_Unit_Cost"
    ];


    const percentageFields = [
        "Cost_Variance_Pct",
        "Avg_Cost_Variance_Pct"
    ];


    const leadTimeFields = [
        "Lead_Time_Days",
        "Avg_Lead_Time_Days"
    ];


    if (currencyFields.includes(key)) {

        return escapeHtml(
            formatCurrency(value)
        );

    }


    if (percentageFields.includes(key)) {

        return (
            `${Number(value || 0).toFixed(1)}%`
        );

    }


    if (leadTimeFields.includes(key)) {

        return (
            `${Number(value || 0).toFixed(1)} days`
        );

    }


    if (
        key === "Risk_Flag"
        || key === "Risk_Level"
    ) {

        const risk =
            String(value || "Low");

        const className =
            `risk-${risk.toLowerCase()}`;


        return (
            `<span class="risk-badge ${className}">`
            + `${escapeHtml(risk)}`
            + `</span>`
        );

    }


    if (
        key === "PO_Date"
        || key === "Requested_Date"
        || key === "Delivery_Date"
    ) {

        return formatDate(value);

    }


    return escapeHtml(value);

}


function renderTable(
    containerId,
    records,
    columns
) {

    const container =
        document.getElementById(containerId);


    if (!records.length) {

        container.innerHTML = (
            '<div class="empty-table">'
            + 'No records found for the selected filters.'
            + '</div>'
        );

        return;

    }


    const headerHtml =
        columns
            .map(
                column => (
                    `<th>${escapeHtml(
                        humanizeColumnName(column)
                    )}</th>`
                )
            )
            .join("");


    const rowsHtml =
        records
            .map(record => {

                const cells =
                    columns
                        .map(
                            column => (
                                `<td>${formatTableCell(
                                    column,
                                    record[column]
                                )}</td>`
                            )
                        )
                        .join("");


                return (
                    `<tr>${cells}</tr>`
                );

            })
            .join("");


    container.innerHTML = `
        <table class="data-table">

            <thead>
                <tr>
                    ${headerHtml}
                </tr>
            </thead>

            <tbody>
                ${rowsHtml}
            </tbody>

        </table>
    `;

}


function currentFilters() {

    return {
        project: projectFilter.value,
        category: categoryFilter.value,
        risk_level: riskFilter.value
    };

}


function populateSelect(
    selectElement,
    records,
    defaultLabel
) {

    const currentValue =
        selectElement.value;


    selectElement.innerHTML =
        `<option value="">${defaultLabel}</option>`;


    records.forEach(record => {

        const option =
            document.createElement("option");

        option.value = record;
        option.textContent = record;

        selectElement.appendChild(option);

    });


    if (
        records.includes(currentValue)
    ) {

        selectElement.value =
            currentValue;

    }

}


async function loadFilters() {

    try {

        const response =
            await fetch("/api/filters");


        if (!response.ok) {

            throw new Error(
                "Unable to load filter options."
            );

        }


        const data =
            await response.json();


        populateSelect(
            projectFilter,
            data.projects,
            "All projects"
        );


        populateSelect(
            categoryFilter,
            data.categories,
            "All categories"
        );


        populateSelect(
            riskFilter,
            data.risk_levels,
            "All risk levels"
        );

    } catch (error) {

        console.error(error);

    }

}


async function fetchDashboardData() {

    const filters =
        currentFilters();


    const params =
        new URLSearchParams();


    Object
        .entries(filters)
        .forEach(([key, value]) => {

            if (value) {

                params.append(
                    key,
                    value
                );

            }

        });


    const response =
        await fetch(
            `/api/dashboard?${params.toString()}`
        );


    if (!response.ok) {

        throw new Error(
            "Unable to load dashboard data."
        );

    }


    return response.json();

}


function updateKpis(kpis) {

    document
        .getElementById("total-cost")
        .textContent =
        formatCurrency(kpis.total_cost);


    document
        .getElementById("budgeted-cost")
        .textContent =
        formatCurrency(kpis.budgeted_cost);


    document
        .getElementById("cost-variance")
        .textContent =
        formatCurrency(kpis.cost_variance);


    document
        .getElementById("po-count")
        .textContent =
        Number(
            kpis.po_count || 0
        ).toLocaleString();


    document
        .getElementById("avg-lead-time")
        .textContent =
        `${Number(
            kpis.avg_lead_time || 0
        ).toFixed(1)} days`;

}


function drawSupplierChart(records) {

    const data =
        [...records].reverse();


    const layout =
        basePlotLayout();


    layout.margin.l = 145;


    layout.xaxis.tickformat = ".2s";

    layout.yaxis.categoryorder = "array";

    layout.yaxis.categoryarray =
        data.map(
            item => item.Supplier_Name
        );


    Plotly.react(
        "supplier-chart",

        [
            {
                type: "bar",

                orientation: "h",

                x: data.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                y: data.map(
                    item => item.Supplier_Name
                ),

                marker: {
                    color: "#49d6b4"
                },

                hovertemplate:
                    "<b>%{y}</b><br>"
                    + "Total Cost: €%{x:,.0f}"
                    + "<extra></extra>"
            }
        ],

        layout,

        plotConfig
    );

}


function drawProjectChart(records) {

    const data =
        [...records].reverse();


    const layout =
        basePlotLayout();


    layout.margin.l = 130;

    layout.xaxis.tickformat = ".2s";


    Plotly.react(
        "project-chart",

        [
            {
                type: "bar",

                orientation: "h",

                x: data.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                y: data.map(
                    item => item.Project_Name
                ),

                marker: {
                    color: "#6f8cff"
                },

                hovertemplate:
                    "<b>%{y}</b><br>"
                    + "Total Cost: €%{x:,.0f}"
                    + "<extra></extra>"
            }
        ],

        layout,

        plotConfig
    );

}


function drawTrendChart(records) {

    const layout =
        basePlotLayout();


    layout.yaxis.tickformat = ".2s";

    layout.xaxis.tickangle = -35;


    Plotly.react(
        "trend-chart",

        [
            {
                type: "scatter",

                mode: "lines+markers",

                x: records.map(
                    item => item.PO_Month
                ),

                y: records.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                line: {
                    color: "#49d6b4",
                    width: 3
                },

                marker: {
                    size: 5
                },

                hovertemplate:
                    "<b>%{x}</b><br>"
                    + "Total Cost: €%{y:,.0f}"
                    + "<extra></extra>"
            }
        ],

        layout,

        plotConfig
    );

}


function drawCategoryChart(records) {

    const layout =
        basePlotLayout();


    layout.showlegend = true;

    layout.legend = {
        orientation: "v",
        x: 1,
        y: 0.5
    };


    Plotly.react(
        "category-chart",

        [
            {
                type: "pie",

                labels: records.map(
                    item =>
                        item.Material_Category
                ),

                values: records.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                hole: 0.62,

                textinfo: "percent",

                hovertemplate:
                    "<b>%{label}</b><br>"
                    + "Total Cost: €%{value:,.0f}<br>"
                    + "%{percent}"
                    + "<extra></extra>"
            }
        ],

        layout,

        plotConfig
    );

}


function drawAnomalyChart(records) {

    const normal =
        records.filter(
            item => !item.Is_Anomaly
        );


    const anomalies =
        records.filter(
            item => item.Is_Anomaly
        );


    const layout =
        basePlotLayout();


    layout.margin.l = 75;


    layout.xaxis = {
        ...layout.xaxis,

        title: "Unit Cost",

        tickprefix: "€",

        tickformat: ".2s"
    };


    layout.yaxis = {
        ...layout.yaxis,

        title: "Total Cost",

        tickprefix: "€",

        tickformat: ".2s"
    };


    Plotly.react(
        "anomaly-chart",

        [
            {
                type: "scatter",

                mode: "markers",

                name: "Normal",

                x: normal.map(
                    item => Number(
                        item.Unit_Cost
                    )
                ),

                y: normal.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                customdata:
                    normal.map(
                        item => [
                            item.PO_Number,
                            item.Supplier_Name,
                            item.Material_Category
                        ]
                    ),

                marker: {
                    size: 6,
                    color: "#49d6b4",
                    opacity: 0.55
                },

                hovertemplate:
                    "<b>%{customdata[0]}</b><br>"
                    + "Supplier: %{customdata[1]}<br>"
                    + "Category: %{customdata[2]}<br>"
                    + "Unit Cost: €%{x:,.2f}<br>"
                    + "Total Cost: €%{y:,.0f}"
                    + "<extra></extra>"
            },


            {
                type: "scatter",

                mode: "markers",

                name: "Anomaly",

                x: anomalies.map(
                    item => Number(
                        item.Unit_Cost
                    )
                ),

                y: anomalies.map(
                    item => Number(
                        item.Total_Cost
                    )
                ),

                customdata:
                    anomalies.map(
                        item => [
                            item.PO_Number,
                            item.Supplier_Name,
                            item.Material_Category
                        ]
                    ),

                marker: {
                    size: 8,
                    color: "#ff647c",
                    opacity: 0.9
                },

                hovertemplate:
                    "<b>%{customdata[0]}</b><br>"
                    + "Supplier: %{customdata[1]}<br>"
                    + "Category: %{customdata[2]}<br>"
                    + "Unit Cost: €%{x:,.2f}<br>"
                    + "Total Cost: €%{y:,.0f}"
                    + "<extra></extra>"
            }
        ],

        layout,

        plotConfig
    );

}


function renderDataTables(data) {

    renderTable(
        "cost-overruns-table",

        data.cost_overruns,

        [
            "Project_Name",
            "Total_Cost",
            "Budgeted_Cost",
            "Cost_Variance",
            "Avg_Cost_Variance_Pct"
        ]
    );


    renderTable(
        "supplier-scorecard-table",

        data.supplier_scorecard,

        [
            "Supplier_Name",
            "Total_Cost",
            "PO_Count",
            "Avg_Lead_Time_Days",
            "Avg_Cost_Variance_Pct",
            "High_Risk_Orders",
            "Risk_Flag"
        ]
    );


    renderTable(
        "raw-data-table",

        data.raw_preview,

        [
            "Project_Name",
            "Supplier_Name",
            "Material_Category",
            "PO_Number",
            "PO_Date",
            "Total_Cost",
            "Cost_Variance_Pct",
            "Lead_Time_Days",
            "Risk_Level"
        ]
    );

}


async function loadDashboard() {

    try {

        const data =
            await fetchDashboardData();


        updateKpis(
            data.kpis
        );


        drawSupplierChart(
            data.suppliers
        );


        drawProjectChart(
            data.projects
        );


        drawTrendChart(
            data.monthly_trends
        );


        drawCategoryChart(
            data.categories
        );


        drawAnomalyChart(
            data.anomalies
        );


        renderDataTables(data);


        document
            .getElementById("anomaly-count")
            .textContent =
            data.anomaly_summary.count;


        document
            .getElementById("anomaly-rate")
            .textContent =
            `${Number(
                data.anomaly_summary.rate
            ).toFixed(1)}%`;


        document
            .getElementById("highest-cost-ratio")
            .textContent =
            `${Number(
                data.anomaly_summary.highest_cost_ratio
            ).toFixed(2)}x`;

    } catch (error) {

        console.error(error);

    }

}


function formatInlineMarkdown(text) {

    return text.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

}


function assistantResponseToHtml(text) {

    const safeText =
        escapeHtml(text);


    return safeText
        .split("\n")
        .map(line => {

            if (
                line.startsWith("### ")
            ) {

                return (
                    '<div class="assistant-response-title">'
                    + formatInlineMarkdown(
                        line.slice(4)
                    )
                    + "</div>"
                );

            }


            if (
                line.startsWith("- ")
            ) {

                return (
                    '<div class="assistant-bullet">'
                    + "• "
                    + formatInlineMarkdown(
                        line.slice(2)
                    )
                    + "</div>"
                );

            }


            return (
                `<div>${formatInlineMarkdown(line)}</div>`
            );

        })
        .join("");

}


function addMessage(
    role,
    text
) {

    const message =
        document.createElement("div");


    message.classList.add(
        "message",

        role === "user"
            ? "user-message"
            : "assistant-message"
    );


    if (
        role === "assistant"
    ) {

        message.innerHTML =
            assistantResponseToHtml(text);

    } else {

        message.textContent =
            text;

    }


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


async function askAssistant(question) {

    addMessage(
        "user",
        question
    );


    const loadingMessage =
        document.createElement("div");


    loadingMessage.className =
        "message assistant-message";


    loadingMessage.textContent =
        "Analysing procurement data...";


    chatMessages.appendChild(
        loadingMessage
    );


    try {

        const response =
            await fetch(
                "/api/assistant",

                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            query: question,
                            filters: currentFilters()
                        }
                    )
                }
            );


        if (!response.ok) {

            throw new Error(
                "Assistant request failed."
            );

        }


        const data =
            await response.json();


        loadingMessage.remove();


        addMessage(
            "assistant",
            data.response
        );

    } catch (error) {

        loadingMessage.textContent =
            "I could not analyse the data. Please try again.";


        console.error(error);

    }

}


/* NAVIGATION */

navItems.forEach(
    navItem => {

        navItem.addEventListener(
            "click",
            () => {

                const targetId =
                    navItem.dataset.target;


                const target =
                    document.getElementById(
                        targetId
                    );


                if (target) {

                    target.scrollIntoView(
                        {
                            behavior: "smooth",
                            block: "start"
                        }
                    );

                }


                navItems.forEach(
                    item =>
                        item.classList.remove(
                            "active"
                        )
                );


                navItem.classList.add(
                    "active"
                );

            }
        );

    }
);


/* TABLE TABS */

tableTabs.forEach(
    tab => {

        tab.addEventListener(
            "click",
            () => {

                const targetId =
                    tab.dataset.tab;


                tableTabs.forEach(
                    item =>
                        item.classList.remove(
                            "active"
                        )
                );


                tablePanels.forEach(
                    panel =>
                        panel.classList.remove(
                            "active"
                        )
                );


                tab.classList.add(
                    "active"
                );


                document
                    .getElementById(targetId)
                    .classList.add(
                        "active"
                    );

            }
        );

    }
);


/* ASSISTANT */

assistantForm.addEventListener(
    "submit",

    async event => {

        event.preventDefault();


        const question =
            assistantInput.value.trim();


        if (!question) {

            return;

        }


        assistantInput.value = "";


        await askAssistant(
            question
        );

    }
);


suggestionToggle.addEventListener(
    "click",

    () => {

        suggestionMenu.classList.toggle(
            "hidden"
        );

    }
);


suggestionMenu
    .querySelectorAll("button")
    .forEach(button => {

        button.addEventListener(
            "click",

            async () => {

                const question =
                    button.dataset.question;


                suggestionMenu.classList.add(
                    "hidden"
                );


                await askAssistant(
                    question
                );

            }
        );

    }
);


/* DASHBOARD CONTROLS */

applyFiltersButton.addEventListener(
    "click",
    loadDashboard
);


refreshButton.addEventListener(
    "click",
    loadDashboard
);


/* START APP */

document.addEventListener(
    "DOMContentLoaded",

    async () => {

        await loadFilters();

        await loadDashboard();

    }
);