"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {

        /* ==========================================
         * API
         * ========================================== */

        const PAYMENT_API_URL =
            "/pay-system/v1/transaction-amount";


        /* ==========================================
         * DOM
         * ========================================== */

        const paymentForm =
            document.getElementById(
                "payment-form"
            );

        const accountIdInput =
            document.getElementById(
                "account-id"
            );

        const amountInput =
            document.getElementById(
                "amount"
            );

        const submitButton =
            document.getElementById(
                "payment-submit-button"
            );


        /* Result */

        const paymentResult =
            document.getElementById(
                "payment-result"
            );

        const resultTitle =
            document.getElementById(
                "result-title"
            );

        const resultMessage =
            document.getElementById(
                "result-message"
            );


        /* Success */

        const successResult =
            document.getElementById(
                "success-result"
            );

        const transactionId =
            document.getElementById(
                "transaction-id"
            );


        /* Account */

        const resultAccountId =
            document.getElementById(
                "result-account-id"
            );

        const resultAccountCurrency =
            document.getElementById(
                "result-account-currency"
            );

        const resultAccountBalance =
            document.getElementById(
                "result-account-balance"
            );

        const resultAccountUpdated =
            document.getElementById(
                "result-account-updated"
            );


        /* Payment */

        const resultPaymentId =
            document.getElementById(
                "result-payment-id"
            );

        const resultPaymentAmount =
            document.getElementById(
                "result-payment-amount"
            );

        const resultPaymentDescription =
            document.getElementById(
                "result-payment-description"
            );

        const resultPaymentCreated =
            document.getElementById(
                "result-payment-created"
            );


        /* Failed */

        const failedResult =
            document.getElementById(
                "failed-result"
            );

        const failedMessage =
            document.getElementById(
                "failed-message"
            );


        /* API Error */

        const errorState =
            document.getElementById(
                "error-state"
            );

        const errorMessage =
            document.getElementById(
                "error-message"
            );


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
                Array.isArray(data.detail)
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
         * Date formatting
         * ========================================== */

        function formatDate(
            value
        ) {

            if (!value) {

                return "—";
            }


            const date =
                new Date(value);


            if (
                Number.isNaN(
                    date.getTime()
                )
            ) {

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


        /* ==========================================
         * Money formatting
         * ========================================== */

        function formatMoney(
            value,
            currency = "RUB"
        ) {

            if (
                value === null ||
                value === undefined
            ) {

                return "—";
            }


            const numericValue =
                Number(value);


            if (
                Number.isNaN(
                    numericValue
                )
            ) {

                return `${value} ${currency}`;
            }


            return (
                new Intl.NumberFormat(
                    "ru-RU",
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }
                ).format(
                    numericValue
                )
                +
                ` ${currency}`
            );
        }


        /* ==========================================
         * Reset result
         * ========================================== */

        function resetResult() {

            paymentResult.hidden =
                true;

            errorState.hidden =
                true;

            successResult.hidden =
                true;

            failedResult.hidden =
                true;

            resultTitle.textContent =
                "Результат операции";

            resultMessage.textContent =
                "";
        }


        /* ==========================================
         * Show API error
         * ========================================== */

        function showError(
            message
        ) {

            errorMessage.textContent =
                message;

            errorState.hidden =
                false;
        }


        /* ==========================================
         * Render successful transaction
         * ========================================== */

        function renderSuccess(
            data
        ) {

            const account =
                data.server?.account;

            const payment =
                data.server?.payment;


            /*
             * Показываем результат.
             */

            paymentResult.hidden =
                false;

            successResult.hidden =
                false;

            failedResult.hidden =
                true;


            /*
             * Заголовок.
             */

            resultTitle.textContent =
                "Операция выполнена";


            /*
             * Сообщение backend.
             */

            resultMessage.textContent =
                data.msg || "";


            /*
             * Transaction ID
             */

            transactionId.textContent =
                data.transaction_id ?? "—";


            /*
             * Account
             */

            resultAccountId.textContent =
                account?.id ?? "—";


            resultAccountCurrency.textContent =
                account?.currency ?? "—";


            resultAccountBalance.textContent =
                formatMoney(
                    account?.balance,
                    account?.currency
                );


            resultAccountUpdated.textContent =
                formatDate(
                    account?.updated
                );


            /*
             * Payment
             */

            resultPaymentId.textContent =
                payment?.id ?? "—";


            resultPaymentAmount.textContent =
                formatMoney(
                    payment?.amount,
                    account?.currency
                );


            resultPaymentDescription.textContent =
                payment?.description || "—";


            resultPaymentCreated.textContent =
                formatDate(
                    payment?.created
                );
        }


        /* ==========================================
         * Render failed transaction
         * ========================================== */

        function renderFailed(
            data
        ) {

            paymentResult.hidden =
                false;

            successResult.hidden =
                true;

            failedResult.hidden =
                false;


            /*
             * Заголовок.
             */

            resultTitle.textContent =
                "Операция не выполнена";


            /*
             * Основное сообщение.
             */

            resultMessage.textContent =
                data.msg || "";


            /*
             * Сообщение сервера.
             */

            failedMessage.textContent =
                data.server?.message ||
                "Сервер не сообщил причину ошибки.";
        }


        /* ==========================================
         * Execute payment
         * ========================================== */

        async function executePayment(
            accountId,
            amount
        ) {

            /*
             * Формируем query parameters.
             */

            const params =
                new URLSearchParams(
                    {
                        amount:
                            String(amount),

                        account_id:
                            accountId
                    }
                );


            const url =
                `${PAYMENT_API_URL}?${params.toString()}`;


            const response =
                await fetch(
                    url,
                    {
                        method: "GET",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        credentials:
                            "same-origin"
                    }
                );


            /*
             * Не авторизован.
             */

            if (
                response.status === 401
            ) {

                window.location.href =
                    "/dev";

                return null;
            }


            /*
             * Пытаемся получить JSON.
             */

            let data = null;


            try {

                data =
                    await response.json();

            } catch (error) {

                console.error(
                    "Invalid JSON response:",
                    error
                );
            }


            /*
             * HTTP error.
             */

            if (
                !response.ok
            ) {

                throw new Error(
                    getApiErrorMessage(
                        data
                    )
                );
            }


            return data;
        }


        /* ==========================================
         * Form submit
         * ========================================== */

        paymentForm.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();


                resetResult();


                /*
                 * Получаем значения.
                 */

                const accountId =
                    accountIdInput.value
                        .trim();


                const amountValue =
                    amountInput.value
                        .trim();


                /*
                 * Валидация account_id.
                 */

                if (!accountId) {

                    showError(
                        "Укажите идентификатор счета."
                    );

                    return;
                }


                /*
                 * Валидация amount.
                 */

                if (!amountValue) {

                    showError(
                        "Укажите сумму операции."
                    );

                    return;
                }


                const amount =
                    Number(
                        amountValue
                    );


                if (
                    !Number.isFinite(
                        amount
                    )
                ) {

                    showError(
                        "Сумма операции должна быть числом."
                    );

                    return;
                }


                if (
                    amount === 0
                ) {

                    showError(
                        "Сумма операции не может быть равна нулю."
                    );

                    return;
                }


                /*
                 * Подтверждение операции.
                 *
                 * GET здесь фактически инициирует
                 * денежную операцию.
                 */

                const confirmed =
                    window.confirm(
                        `Выполнить операцию на сумму ${amount} ₽?`
                    );


                if (!confirmed) {

                    return;
                }


                /*
                 * Блокируем кнопку.
                 */

                submitButton.disabled =
                    true;

                submitButton.textContent =
                    "Выполнение...";


                try {

                    const data =
                        await executePayment(
                            accountId,
                            amount
                        );


                    /*
                     * Если executePayment
                     * сделал redirect после 401.
                     */

                    if (!data) {

                        return;
                    }


                    /*
                     * Успешная операция.
                     *
                     * Есть account и payment.
                     */

                    if (
                        data.server?.account &&
                        data.server?.payment
                    ) {

                        renderSuccess(
                            data
                        );

                        return;
                    }


                    /*
                     * Операция не выполнена.
                     *
                     * Например:
                     *
                     * server:
                     * {
                     *     message:
                     *     "Для выполнения операции..."
                     * }
                     */

                    if (
                        data.server?.message
                    ) {

                        renderFailed(
                            data
                        );

                        return;
                    }


                    /*
                     * Неожиданный формат.
                     */

                    showError(
                        "Сервер вернул неизвестный формат ответа."
                    );


                } catch (error) {

                    console.error(
                        "Payment error:",
                        error
                    );


                    showError(
                        error.message ||
                        "Не удалось выполнить платежную операцию."
                    );


                } finally {

                    submitButton.disabled =
                        false;

                    submitButton.textContent =
                        "Выполнить операцию";
                }

            }
        );

    }
);