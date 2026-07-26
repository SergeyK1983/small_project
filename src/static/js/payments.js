"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* API */
        const PAYMENTS_API_BASE_URL = "/pay-system/v1/user-cash-payments";

        /* DOM */
        const loadingState = document.getElementById("loading-state");
        const errorState = document.getElementById("error-state");
        const paymentsContent = document.getElementById("payments-content");
        const errorMessage = document.getElementById("error-message");
        const retryButton = document.getElementById("retry-button");
        const paymentsTableBody = document.getElementById("payments-table-body");
        const emptyPayments = document.getElementById("empty-payments");
        const accountIdElement = document.getElementById("account-id");
        const accountInfo = document.getElementById("account-info");


        /* Get account ID from URL /dev/accounts/{account_id}/payments */
        function getAccountIdFromUrl() {
            const pathParts = window.location.pathname.split("/").filter(Boolean);

            /* Ожидаем: ["dev", "accounts", "{account_id}", "payments"] */
            if (pathParts.length !== 4 || pathParts[0] !== "dev" || pathParts[3] !== "payments") {
                return null;
            }
            return pathParts[2];
        }

        const accountId = getAccountIdFromUrl();

        /* Page state */
        function showState(state) {
            loadingState.hidden = state !== "loading";
            errorState.hidden = state !== "error";
            paymentsContent.hidden = state !== "content";
        }

        /* API error */
        function getApiErrorMessage(data) {
            if (!data) {
                return ("Произошла неизвестная ошибка.");
            }

            if (typeof data.detail === "string") {
                return data.detail;
            }

            if (Array.isArray(data.detail)) {
                return data.detail
                    .map(error => error.msg || "Ошибка валидации.")
                    .join(" ");
            }

            if (typeof data.message === "string") {
                return data.message;
            }

            return (
                "Произошла ошибка. " +
                "Попробуйте еще раз."
            );
        }

        /*  Date formatting */
        function formatDate(value) {
            if (!value) {
                return "—";
            }

            const date = new Date(value);

            if (Number.isNaN(date.getTime())) {
                return value;
            }

            return new Intl.DateTimeFormat(
                "ru-RU",
                {
                    dateStyle: "short",
                    timeStyle: "short"
                }
            ).format(date);
        }

        /* Amount formatting */
        function formatAmount(amount) {

            if (amount === null || amount === undefined) {
                return {
                    text: "—",
                    type: "neutral"
                };
            }            

            const numericAmount = Number(amount);

            if (Number.isNaN(numericAmount)) {
                return {
                    text: String(amount),
                    type: "neutral"
                };
            }

            const formattedAmount =
                new Intl.NumberFormat(
                    "ru-RU",
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }
                ).format(
                    Math.abs(
                        numericAmount
                    )
                );


            /* Положительная операция. */
            if (numericAmount > 0) {
                return {
                    text:
                        `+${formattedAmount} ₽`,
                    type: "income"
                };
            }

            /* Отрицательная операция. */
            if (numericAmount < 0) {
                return {
                    text:
                        `−${formattedAmount} ₽`,
                    type: "expense"
                };
            }

            /* Нулевая операция. */
            return {
                text:
                    "0,00 ₽",
                type: "neutral"
            };
        }

        /* Create table cell */
        function createCell(value) {

            const cell = document.createElement("td");

            cell.textContent = value ?? "—";
            return cell;
        }

        /* Create amount cell */
        function createAmountCell(amount) {

            const cell = document.createElement("td");
            const amountData = formatAmount(amount);

            cell.textContent = amountData.text;

            cell.classList.add("payment-amount");
            cell.classList.add(`payment-amount-${amountData.type}`);
            return cell;
        }

        /* Render payments */
        function renderPayments(data) {

            /* Account ID */
            accountIdElement.textContent = data.account_id ?? "—";

            /* Header info */
            accountInfo.textContent = `Всего операций: ${data.payments?.length ?? 0}`;

            /* Clear table */
            paymentsTableBody.replaceChildren();

            /* Empty list */
            if (!data.payments || data.payments.length === 0) {
                emptyPayments.hidden = false;
                return;
            }

            emptyPayments.hidden = true;

            /* Create rows */
            for (
                const payment
                of data.payments
            ) {

                const row =
                    document.createElement(
                        "tr"
                    );

                /* Created */
                row.appendChild(
                    createCell(
                        formatDate(
                            payment.created
                        )
                    )
                );

                /* Description */
                row.appendChild(
                    createCell(
                        payment.description
                    )
                );

                /* Amount */
                row.appendChild(
                    createAmountCell(
                        payment.amount
                    )
                );

                /* Payment ID */
                const paymentIdCell = createCell(payment.id);

                paymentIdCell.classList.add("payment-id");
                row.appendChild(paymentIdCell);

                /* Transaction ID */
                const transactionIdCell = createCell(payment.transaction_id);

                transactionIdCell.classList.add("payment-id");
                row.appendChild(transactionIdCell);

                /* Account ID */
                const accountIdCell = createCell(payment.account_rub_id);

                accountIdCell.classList.add("payment-id");
                row.appendChild(accountIdCell);

                /* Add row */
                paymentsTableBody.appendChild(row);
            }
        }


        /*  Load payments */
        async function loadPayments() {
            showState("loading");

            /* Проверяем account_id. */
            if (!accountId) {
                errorMessage.textContent = "Не удалось определить идентификатор счета.";
                showState("error");
                return;
            }

            /* Формируем API URL. */
            const apiUrl = `${PAYMENTS_API_BASE_URL}/${encodeURIComponent(accountId)}`;

            try {
                const response = await fetch(
                    apiUrl,
                    {
                        method: "GET",
                        headers: {
                            "Accept": "application/json"
                        },
                        credentials: "same-origin"
                    }
                );

                /* Пользователь не авторизован. */
                if (response.status === 401) {
                    window.location.href = "/dev";
                    return;
                }

                const data = await response.json();

                /* Backend error. */
                if (!response.ok) {
                    errorMessage.textContent = getApiErrorMessage(data);
                    showState("error");
                    return;
                }

                /* Render. */
                renderPayments(data);
                showState("content");

            } catch (error) {
                console.error("Load payments error:", error);
                errorMessage.textContent = "Не удалось подключиться к серверу.";
                showState("error");
            }
        }

        /* Retry */
        retryButton.addEventListener("click", () => {
            loadPayments();
        });

        /*  Initial load */
        loadPayments();
    }
);