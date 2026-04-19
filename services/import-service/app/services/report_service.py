from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import HTTPException

from app.db.mongo import import_collection


class ReportService:
    DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
    INPUT_DATE_FORMAT = "%Y-%m-%d"

    # =====================================================
    # PUBLIC METHOD
    # =====================================================
    async def get_summary(self, filters: dict):
        mode = filters.get("mode")
        stores = filters.get("stores")

        if mode:
            self._validate_filters(mode, filters)

        pipeline = self._build_pipeline(mode, stores, filters)
        reports = await import_collection.aggregate(pipeline).to_list(None)

        result = self._process_reports(reports, mode)

        return self._format_result(result)

    # =====================================================
    # MONGO PIPELINE
    # =====================================================
    def _build_pipeline(self, mode: str, stores: list, filters: dict):
        pipeline = [
            {
                "$addFields": {
                    "parsedDate": {
                        "$dateFromString": {
                            "dateString": "$date",
                            "format": self.DATE_FORMAT,
                        }
                    }
                }
            }
        ]

        match_stage = {}

        if stores:
            match_stage["store"] = {"$in": stores}

        date_filter = self._get_date_filter(mode, filters)

        if date_filter:
            match_stage["parsedDate"] = date_filter

        if match_stage:
            pipeline.append({"$match": match_stage})

        return pipeline

    def _get_date_filter(self, mode: str, filters: dict):
        if mode == "day":
            from_date = datetime.strptime(
                filters["fromDate"], self.INPUT_DATE_FORMAT
            )
            to_date = datetime.strptime(
                filters["toDate"], self.INPUT_DATE_FORMAT
            ) + timedelta(days=1)

            return {"$gte": from_date, "$lte": to_date}

        if mode == "week":
            month = int(filters["month"])
            year = int(filters["year"])

            start = datetime(year, month, 1)

            end = (
                datetime(year + 1, 1, 1)
                if month == 12
                else datetime(year, month + 1, 1)
            )

            return {"$gte": start, "$lt": end}

        if mode in ("month", "year"):
            year = int(filters["year"])

            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)

            return {"$gte": start, "$lt": end}

        return None

    # =====================================================
    # PROCESS REPORTS
    # =====================================================
    def _process_reports(self, reports: list, mode: str):
        result = {}

        for report in reports:
            report_date = report.get("parsedDate")

            if not report_date:
                continue

            store = report.get("store", "unknown")
            key = self._get_time_key(report_date, mode)

            if store not in result:
                result[store] = defaultdict(self._default_group)

            groups = report.get("groups", {})

            self._process_payment(result, store, key, groups)
            self._process_finance(result, store, key, groups)
            self._process_sales(result, store, key, groups)
            self._process_exclusive(result, store, key, groups)
            self._process_promo(result, store, key, groups)
            self._process_scratch_card(result, store, key, groups, mode)

        return result

    def _default_group(self):
        return {
            "payment_summary": {},
            "sales_summary": {},
            "exclusive_departments": {},
            "promotion_discount_refund": {},
            "daily_finance_data": {},
            "scratch_card_data": [],
        }

    # =====================================================
    # GROUP PROCESSORS
    # =====================================================
    def _process_payment(self, result, store, key, groups):
        for item in groups.get("payment_summary", []):
            name = item.get("name")
            amount = float(item.get("amount", 0))

            self._add_amount(
                result[store]["all"]["payment_summary"],
                name,
                amount,
            )

            self._add_amount(
                result[store][key]["payment_summary"],
                name,
                amount,
            )

    def _process_finance(self, result, store, key, groups):
        for name, value in groups.get(
            "daily_finance_data",
            {}
        ).items():
            amount = float(value)

            self._add_amount(
                result[store]["all"]["daily_finance_data"],
                name,
                amount,
            )

            self._add_amount(
                result[store][key]["daily_finance_data"],
                name,
                amount,
            )

    def _process_sales(self, result, store, key, groups):
        for item in groups.get("sales_summary", []):
            self._update_qty_amount(
                result[store],
                key,
                "sales_summary",
                item,
            )

    def _process_exclusive(self, result, store, key, groups):
        for item in groups.get(
            "exclusive_departments",
            []
        ):
            self._update_dynamic_group(
                result[store],
                key,
                "exclusive_departments",
                item,
            )

    def _process_promo(self, result, store, key, groups):
        for item in groups.get(
            "promotion_discount_refund",
            []
        ):
            name = item.get("name")
            amount = float(item.get("amount", 0))

            self._add_amount(
                result[store]["all"][
                    "promotion_discount_refund"
                ],
                name,
                amount,
            )

            self._add_amount(
                result[store][key][
                    "promotion_discount_refund"
                ],
                name,
                amount,
            )

    def _process_scratch_card(
        self,
        result,
        store,
        key,
        groups,
        mode,
    ):
        if mode != "day":
            return

        for item in groups.get(
            "scratch_card_data",
            []
        ):
            result[store][key][
                "scratch_card_data"
            ].append(
                {
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "open": item.get("open"),
                    "close": item.get("close"),
                    "sales": item.get("sales"),
                    "amount": item.get("amount"),
                    "issues": item.get("issue"),
                    "ref": item.get("ref"),
                }
            )

    # =====================================================
    # HELPERS
    # =====================================================
    def _update_qty_amount(
        self,
        store_data,
        key,
        section,
        item,
    ):
        name = item.get("name")
        qty = int(item.get("qty", 0))
        amount = float(item.get("amount", 0))

        self._add_qty_amount(
            store_data["all"][section],
            name,
            qty,
            amount,
        )

        self._add_qty_amount(
            store_data[key][section],
            name,
            qty,
            amount,
        )

    def _update_dynamic_group(
        self,
        store_data,
        key,
        section,
        item,
    ):
        name = item.get("name")

        self._add_dynamic_fields(
            store_data["all"][section],
            name,
            item,
        )

        self._add_dynamic_fields(
            store_data[key][section],
            name,
            item,
        )

    def _add_amount(
        self,
        container,
        key,
        amount,
    ):
        if not key:
            return

        container[key] = (
            container.get(key, 0) + amount
        )

    def _add_qty_amount(
        self,
        container,
        key,
        qty,
        amount,
    ):
        if not key:
            return

        if key not in container:
            container[key] = {
                "qty": 0,
                "amount": 0,
            }

        container[key]["qty"] += qty
        container[key]["amount"] += amount

    def _add_dynamic_fields(
        self,
        container,
        key,
        item,
    ):
        if not key:
            return

        if key not in container:
            container[key] = {}

        for field, value in item.items():
            if field == "name":
                continue

            try:
                num = float(value)
            except (
                TypeError,
                ValueError,
            ):
                continue

            container[key][field] = (
                container[key].get(field, 0)
                + num
            )

    # =====================================================
    # VALIDATION
    # =====================================================
    def _validate_filters(
        self,
        mode,
        filters,
    ):
        if mode == "day":
            if (
                not filters.get("fromDate")
                or not filters.get("toDate")
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "fromDate and toDate required"
                    ),
                )

        elif mode == "week":
            if (
                not filters.get("month")
                or not filters.get("year")
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "month and year required"
                    ),
                )

        elif mode in (
            "month",
            "year",
        ):
            if not filters.get("year"):
                raise HTTPException(
                    status_code=400,
                    detail="year required",
                )

        else:
            raise HTTPException(
                status_code=400,
                detail="invalid mode",
            )

    # =====================================================
    # TIME KEY
    # =====================================================
    def _get_time_key(
        self,
        date_obj,
        mode,
    ):
        if not mode:
            return "all"

        if mode == "day":
            return date_obj.strftime(
                "%Y-%m-%d"
            )

        if mode == "week":
            month = date_obj.strftime("%b")
            year = date_obj.year
            day = date_obj.day

            if day <= 7:
                return (
                    f"W1 - 1 to 7 / "
                    f"{month} / {year}"
                )

            if day <= 14:
                return (
                    f"W2 - 8 to 14 / "
                    f"{month} / {year}"
                )

            if day <= 21:
                return (
                    f"W3 - 15 to 21 / "
                    f"{month} / {year}"
                )

            return (
                f"W4 - 22 to 31 / "
                f"{month} / {year}"
            )

        if mode == "month":
            return date_obj.strftime(
                "%b / %Y"
            )

        if mode == "year":
            return str(date_obj.year)

        return "all"

    # =====================================================
    # FORMAT OUTPUT
    # =====================================================
    def _format_result(self, result):
        final = []

        for store, store_data in result.items():
            formatted = {}

            for key, value in store_data.items():
                formatted[key] = {
                    "payment_summary":
                        self._amount_list(
                            value[
                                "payment_summary"
                            ]
                        ),

                    "sales_summary":
                        self._qty_amount_list(
                            value[
                                "sales_summary"
                            ]
                        ),

                    "exclusive_departments":
                        self._dynamic_list(
                            value[
                                "exclusive_departments"
                            ]
                        ),

                    "promotion_discount_refund":
                        self._amount_list(
                            value[
                                "promotion_discount_refund"
                            ]
                        ),

                    "daily_finance_data":
                        self._amount_list(
                            value[
                                "daily_finance_data"
                            ]
                        ),

                    "scratch_card_data":
                        value[
                            "scratch_card_data"
                        ],
                }

            final.append(
                {
                    "store": store,
                    "data": formatted,
                }
            )

        return final

    def _amount_list(self, data):
        return [
            {
                "name": key,
                "amount": value,
            }
            for key, value in data.items()
        ]

    def _qty_amount_list(self, data):
        return [
            {
                "name": key,
                "qty": value["qty"],
                "amount": value["amount"],
            }
            for key, value in data.items()
        ]

    def _dynamic_list(self, data):
        return [
            {
                "name": key,
                **value,
            }
            for key, value in data.items()
        ]