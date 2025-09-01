# CLI 환경에서 VendingMachine 기능 테스트
from core.vending_machine import VendingMachine

def print_menu():
    print("\n====== 자판기 메뉴 ======")
    print("1. 돈 투입")
    print("2. 선택 가능한 음료 보기")
    print("3. 음료 구매")
    print("4. 입력 취소 및 환불")
    print("5. 자판기 상태 확인 (디버깅용)")
    print("0. 종료")

def main():
    vm = VendingMachine()

    while True:
        print_menu()
        choice = input("메뉴 선택: ").strip()

        if choice == "1":
            try:
                amount = int(input("투입할 금액 (10, 50, 100, 500, 1000만 가능): "))
                msg = vm.insert_money(amount)
                print(msg)
            except ValueError:
                print("숫자를 입력해주세요.")

        elif choice == "2":
            available = vm.get_available_beverages()
            if not available:
                print("구매 가능한 음료가 없습니다.")
            else:
                print("=== 구매 가능한 음료 ===")
                for bev in available:
                    print(f"{bev['name']} - {bev['price']}원 ({bev['stock']}개 남음)")

        elif choice == "3":
            name = input("구매할 음료 이름 입력: ").strip()
            result = vm.purchase(name)
            print(result)

        elif choice == "4":
            refund = vm.cancel_transaction()
            print(refund)

        elif choice == "5":
            status = vm.get_status()
            print("현재 재고:")
            for b in status['beverages']:
                print(f"  {b['name']}: {b['stock']}개 남음")
            print("현재 동전 상태:")
            for coin, count in status['coins'].items():
                print(f"  {coin}원: {count}개")

        elif choice == "0":
            print("자판기 프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    main()