"use strict";


document.addEventListener("DOMContentLoaded", () => {
    /* API */
    const ACCOUNTS_API_URL = "/pay-system/v1/user-cash-accounts";

    /* HTML routes */
    const PAYMENTS_PAGE_URL = "/dev/accounts";

    /* DOM */
    const loadingState = document.getElementById("loading-state");
    const errorState = document.getElementById("error-state");
    const accountsContent = document.getElementById("accounts-content");
    const errorMessage = document.getElementById("error-message");
    const retryButton = document.getElementById("retry-button");
    const accountsTableBody = document.getElementById("accounts-table-body");
    const emptyAccounts = document.getElementById("empty-accounts");
    const userId = document.getElementById("user-id");
    const accountsUserInfo = document.getElementById("accounts-user-info");

    /* Page */
    function showState(state) {
        loadingState.hidden = state !== "loading";
        errorState.hidden = state !== "error";
        accountsContent.hidden = state !== "content";
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

    /* Date formatting */
    function formatDate(value) {
        if (!value) {
            return "—";            }


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

    /* Balance formatting */
    function formatBalance(balance, currency) {
        if (balance === null || balance === undefined) {
            return "—";
        }            

        const numericBalance = Number(balance);

        if (Number.isNaN(numericBalance)) {
            return `${balance}`;
            /*return `${balance} ${currency}`;*/
        }

        return (
            new Intl.NumberFormat(
                "ru-RU",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            ).format(
                numericBalance
            )
            /*+
            ` ${currency}`*/
        );
    }

    /* Create table cell */
    function createCell(value) {

        const cell = document.createElement("td");
        cell.textContent = value ?? "—";
        return cell;
    }

    /* Render accounts */
    function renderAccounts(data) {
        
        /* User ID */
        userId.textContent = data.user_id ?? "—";

        /* Заголовок */
        accountsUserInfo.textContent =
            `Всего счетов: ${
                data.accounts?.length ?? 0
            }`;

        /* Очищаем таблицу */
        accountsTableBody.replaceChildren();

        /* Проверяем наличие счетов */
        if (!data.accounts || data.accounts.length === 0) {

            emptyAccounts.hidden = false;
            return;
        }

        emptyAccounts.hidden = true;

        /* Создаём строки */
        for (
            const account
            of data.accounts
        ) {

            const row = document.createElement("tr");

            /* Account ID */
            row.appendChild(createCell(account.id));

            /* Currency */
            row.appendChild(createCell(account.currency));

            /* Balance */
            row.appendChild(
                createCell(
                    formatBalance(
                        account.balance,
                        account.currency
                    )
                )
            );

            /* Created */
            row.appendChild(
                createCell(
                    formatDate(
                        account.created
                    )
                )
            );

            /* Updated */
            row.appendChild(
                createCell(
                    formatDate(
                        account.updated
                    )
                )
            );

            /* Payments link */
            const paymentsCell = document.createElement("td");
            const paymentsLink = document.createElement("a");

            paymentsLink.href = `${PAYMENTS_PAGE_URL}/${account.id}/payments`;
            paymentsLink.textContent = "Операции";
            paymentsLink.classList.add("table-action-link");

            paymentsCell.appendChild(paymentsLink);

            row.appendChild(paymentsCell);

            /* Добавляем строку */
            accountsTableBody.appendChild(row);
        }
    }

    /*  Load accounts */
    async function loadAccounts() {
        showState("loading");

        try {
            const response = await fetch(
                ACCOUNTS_API_URL,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    },
                    credentials: "same-origin"
                }
            );

            /* Авторизация отсутствует.*/
            if (response.status === 401) {
                window.location.href = "/dev";
                return;
            }

            const data = await response.json();

            /* Backend error */
            if (!response.ok) {
                errorMessage.textContent = getApiErrorMessage(data);
                showState("error");
                return;
            }

            /* Render */
            renderAccounts(data);

            showState("content");

        } catch (error) {
            console.error("Load accounts error:", error);

            errorMessage.textContent = "Не удалось подключиться к серверу.";

            showState("error");
        }
    }

    /*  Retry */
    retryButton.addEventListener("click", () => {
        loadAccounts();
    });

    /* Initial load */
    loadAccounts();
});
