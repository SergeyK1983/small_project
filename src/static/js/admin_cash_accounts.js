"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* ==========================================
         * API
         * ========================================== */

        const ACCOUNTS_API_URL =
            "/pay-system/v1/adm-cash-accounts-user";

        const CREATE_ACCOUNT_API_URL =
            "/pay-system/v1/create-cash-account";


        /* ==========================================
         * URL parameters
         * ========================================== */

        const params =
            new URLSearchParams(
                window.location.search
            );


        const userId =
            params.get(
                "user_id"
            );


        /* ==========================================
         * DOM
         * ========================================== */

        const loadingState =
            document.getElementById(
                "loading-state"
            );


        const errorState =
            document.getElementById(
                "error-state"
            );


        const accountsContent =
            document.getElementById(
                "accounts-content"
            );


        const errorMessage =
            document.getElementById(
                "error-message"
            );


        const retryButton =
            document.getElementById(
                "retry-button"
            );


        const userDescription =
            document.getElementById(
                "user-description"
            );


        const userIdElement =
            document.getElementById(
                "user-id"
            );


        const emptyAccounts =
            document.getElementById(
                "empty-accounts"
            );


        const accountsTableWrapper =
            document.getElementById(
                "accounts-table-wrapper"
            );


        const accountsTableBody =
            document.getElementById(
                "accounts-table-body"
            );


        const createAccountButton =
            document.getElementById(
                "create-account-button"
            );


        const createAccountMessage =
            document.getElementById(
                "create-account-message"
            );


        /* ==========================================
         * Page state
         * ========================================== */

        function showState(
            state
        ) {

            loadingState.hidden =
                state !== "loading";


            errorState.hidden =
                state !== "error";


            accountsContent.hidden =
                state !== "content";

        }


        /* ==========================================
         * API error
         * ========================================== */

        function getApiErrorMessage(
            data
        ) {

            if (!data) {

                return (
                    "Произошла неизвестная ошибка."
                );

            }


            if (
                typeof data.detail ===
                "string"
            ) {

                return data.detail;

            }


            if (
                Array.isArray(
                    data.detail
                )
            ) {

                return data.detail
                    .map(
                        error =>
                            error.msg ||
                            "Ошибка валидации."
                    )
                    .join(" ");

            }


            if (
                typeof data.message ===
                "string"
            ) {

                return data.message;

            }


            return (
                "Произошла ошибка. " +
                "Попробуйте еще раз."
            );

        }


        /* ==========================================
         * Create account message
         * ========================================== */

        function showCreateAccountMessage(
            message,
            type
        ) {

            createAccountMessage.textContent =
                message;


            createAccountMessage.className =
                "action-message";


            if (
                type === "success"
            ) {

                createAccountMessage.classList.add(
                    "action-message-success"
                );

            } else {

                createAccountMessage.classList.add(
                    "action-message-error"
                );

            }


            createAccountMessage.hidden =
                false;

        }


        /* ==========================================
         * Format balance
         * ========================================== */

        function formatBalance(
            balance,
            currency
        ) {

            /*
             * Backend уже сериализует
             * balance в Decimal.
             *
             * Например:
             *
             * "7402.25"
             *
             * или:
             *
             * 7402.25
             */

            const numericBalance =
                Number(
                    balance
                );


            if (
                Number.isNaN(
                    numericBalance
                )
            ) {

                return (
                    `${balance ?? "—"} ${currency ?? ""}`
                );

            }


            try {

                return new Intl.NumberFormat(
                    "ru-RU",
                    {
                        minimumFractionDigits:
                            2,

                        maximumFractionDigits:
                            2
                    }
                ).format(
                    numericBalance
                );

            } catch (error) {

                console.error(
                    "Format balance error:",
                    error
                );


                return String(
                    numericBalance
                );

            }

        }


        /* ==========================================
         * Append account to table
         * ========================================== */

        function appendAccountToTable(
            account
        ) {

            /*
             * Если до создания счёта
             * отображалось сообщение
             * "У пользователя нет платежных счетов",
             * скрываем его.
             */

            emptyAccounts.hidden =
                true;


            /*
             * Показываем таблицу.
             */

            accountsTableWrapper.hidden =
                false;


            /*
             * Создаём строку.
             */

            const row =
                document.createElement(
                    "tr"
                );


            /*
             * Currency
             */

            const currencyCell =
                document.createElement(
                    "td"
                );


            currencyCell.className =
                "account-currency";


            currencyCell.textContent =
                account.currency ??
                "—";


            /*
             * Balance
             */

            const balanceCell =
                document.createElement(
                    "td"
                );


            balanceCell.className =
                "account-balance";


            balanceCell.textContent =
                formatBalance(
                    account.balance,
                    account.currency
                );


            /*
             * Добавляем ячейки
             */

            row.appendChild(
                currencyCell
            );


            row.appendChild(
                balanceCell
            );


            /*
             * Добавляем строку
             * в таблицу.
             */

            accountsTableBody.appendChild(
                row
            );

        }


        /* ==========================================
         * Render accounts
         * ========================================== */

        function renderAccounts(
            data
        ) {

            /*
             * User ID
             */

            userIdElement.textContent =
                data.user_id ??
                "—";


            userDescription.textContent =
                `Счета пользователя ${data.user_id}`;


            /*
             * Очищаем таблицу.
             */

            accountsTableBody.replaceChildren();


            /*
             * Получаем список счетов.
             */

            const accounts =
                Array.isArray(
                    data.accounts
                )
                    ? data.accounts
                    : [];


            /*
             * У пользователя нет счетов.
             */

            if (
                accounts.length ===
                0
            ) {

                emptyAccounts.hidden =
                    false;


                accountsTableWrapper.hidden =
                    true;


                return;

            }


            /*
             * Счета существуют.
             */

            emptyAccounts.hidden =
                true;


            accountsTableWrapper.hidden =
                false;


            /*
             * Формируем строки таблицы.
             */

            accounts.forEach(
                account => {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    /*
                     * Currency
                     */

                    const currencyCell =
                        document.createElement(
                            "td"
                        );


                    currencyCell.className =
                        "account-currency";


                    currencyCell.textContent =
                        account.currency ??
                        "—";


                    /*
                     * Balance
                     */

                    const balanceCell =
                        document.createElement(
                            "td"
                        );


                    balanceCell.className =
                        "account-balance";


                    balanceCell.textContent =
                        formatBalance(
                            account.balance,
                            account.currency
                        );


                    /*
                     * Append cells
                     */

                    row.appendChild(
                        currencyCell
                    );


                    row.appendChild(
                        balanceCell
                    );


                    /*
                     * Append row
                     */

                    accountsTableBody.appendChild(
                        row
                    );

                }
            );

        }


        /* ==========================================
         * Load accounts
         * ========================================== */

        async function loadAccounts() {

            showState(
                "loading"
            );


            /*
             * Проверяем наличие user_id.
             */

            if (!userId) {

                errorMessage.textContent =
                    "Не указан идентификатор пользователя.";


                showState(
                    "error"
                );


                return;

            }


            try {

                const accountsUrl =
                    `${ACCOUNTS_API_URL}/${encodeURIComponent(userId)}`;


                const response =
                    await fetch(
                        accountsUrl,
                        {
                            method:
                                "GET",

                            headers: {
                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin"
                        }
                    );


                /*
                 * Пользователь не авторизован.
                 */

                if (
                    response.status ===
                    401
                ) {

                    window.location.href =
                        "/dev";


                    return;

                }


                /*
                 * Нет прав администратора.
                 */

                if (
                    response.status ===
                    403
                ) {

                    errorMessage.textContent =
                        "У вас нет прав для просмотра счетов пользователя.";


                    showState(
                        "error"
                    );


                    return;

                }


                /*
                 * Получаем JSON.
                 */

                const data =
                    await response.json();


                /*
                 * Ошибка backend.
                 */

                if (
                    !response.ok
                ) {

                    errorMessage.textContent =
                        getApiErrorMessage(
                            data
                        );


                    showState(
                        "error"
                    );


                    return;

                }


                /*
                 * Отображаем данные.
                 */

                renderAccounts(
                    data
                );


                showState(
                    "content"
                );


            } catch (error) {

                console.error(
                    "Load user accounts error:",
                    error
                );


                errorMessage.textContent =
                    "Не удалось подключиться к серверу.";


                showState(
                    "error"
                );

            }

        }


        /* ==========================================
         * Create account
         * ========================================== */

        async function createAccount() {

            /*
             * Проверяем user_id.
             */

            if (!userId) {

                showCreateAccountMessage(
                    "Не указан идентификатор пользователя.",
                    "error"
                );

                return;

            }


            /*
             * Подтверждение действия.
             */

            const confirmed =
                window.confirm(
                    "Создать новый платежный счёт для этого пользователя?"
                );


            if (!confirmed) {

                return;

            }


            /*
             * Блокируем кнопку.
             */

            createAccountButton.disabled =
                true;


            createAccountButton.textContent =
                "Создание...";


            /*
             * Скрываем предыдущее сообщение.
             */

            createAccountMessage.hidden =
                true;


            try {

                const response =
                    await fetch(
                        CREATE_ACCOUNT_API_URL,
                        {
                            method:
                                "POST",

                            headers: {
                                "Accept":
                                    "application/json",

                                "Content-Type":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify(
                                    {
                                        user_id:
                                            userId
                                    }
                                )
                        }
                    );


                /*
                 * Пользователь не авторизован.
                 */

                if (
                    response.status ===
                    401
                ) {

                    window.location.href =
                        "/dev";


                    return;

                }


                /*
                 * Нет прав администратора.
                 */

                if (
                    response.status ===
                    403
                ) {

                    showCreateAccountMessage(
                        "У вас нет прав для создания счёта.",
                        "error"
                    );


                    return;

                }


                /*
                 * Получаем JSON.
                 */

                const data =
                    await response.json();


                /*
                 * Ошибка backend.
                 */

                if (
                    !response.ok
                ) {

                    showCreateAccountMessage(
                        getApiErrorMessage(
                            data
                        ),
                        "error"
                    );


                    return;

                }


                /*
                 * Счёт успешно создан.
                 *
                 * Backend возвращает CashAccountBase,
                 * поэтому можем сразу добавить его
                 * в таблицу.
                 */

                appendAccountToTable(
                    data
                );


                /*
                 * Показываем сообщение.
                 */

                showCreateAccountMessage(
                    `Счёт ${data.currency ?? ""} успешно создан.`,
                    "success"
                );


            } catch (error) {

                console.error(
                    "Create account error:",
                    error
                );


                showCreateAccountMessage(
                    "Не удалось создать счёт. Попробуйте ещё раз.",
                    "error"
                );


            } finally {

                /*
                 * Разблокируем кнопку.
                 */

                createAccountButton.disabled =
                    false;


                createAccountButton.textContent =
                    "Создать счёт";

            }

        }


        /* ==========================================
         * Retry
         * ========================================== */

        retryButton.addEventListener(
            "click",
            () => {

                loadAccounts();

            }
        );


        /* ==========================================
         * Create account button
         * ========================================== */

        createAccountButton.addEventListener(
            "click",
            createAccount
        );


        /* ==========================================
         * Initial load
         * ========================================== */

        loadAccounts();

    }
);