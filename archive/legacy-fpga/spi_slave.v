//============================================================================
// SPI Slave Interface
// CPOL=0, CPHA=0 mode
// 16-bit transfer, MSB first
//============================================================================

module spi_slave (
    input wire clk,                     // System clock
    input wire rst_n,                   // Active-low reset
    input wire sck,                     // SPI clock
    input wire mosi,                    // Master Out Slave In
    output reg miso,                    // Master In Slave Out
    input wire cs_n,                    // Chip select (active low)
    output reg [7:0] rx_data,           // Received data
    input wire [7:0] tx_data,           // Data to transmit
    output reg rx_valid                 // Pulse when rx_data valid
);

    // Synchronize SPI signals to system clock
    reg [1:0] sck_sync;
    reg [1:0] mosi_sync;
    reg [1:0] cs_n_sync;
    
    always @(posedge clk) begin
        sck_sync <= {sck_sync[0], sck};
        mosi_sync <= {mosi_sync[0], mosi};
        cs_n_sync <= {cs_n_sync[0], cs_n};
    end
    
    // Detect SCK edges
    wire sck_rising = (sck_sync == 2'b01);
    wire sck_falling = (sck_sync == 2'b10);
    wire cs_active = ~cs_n_sync[1];
    
    // Bit counter and shift registers
    reg [3:0] bit_cnt;
    reg [15:0] shift_rx;
    reg [15:0] shift_tx;
    reg [15:0] tx_buffer;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sck_sync <= 2'b00;
            mosi_sync <= 2'b00;
            cs_n_sync <= 2'b11;
            bit_cnt <= 0;
            shift_rx <= 0;
            shift_tx <= 0;
            tx_buffer <= 0;
            rx_data <= 0;
            rx_valid <= 0;
            miso <= 0;
        end else begin
            rx_valid <= 0;  // Default: no valid data
            
            if (!cs_active) begin
                // CS inactive: reset state
                bit_cnt <= 0;
                shift_rx <= 0;
                // Load TX buffer when CS goes high (end of previous transfer)
                tx_buffer <= {tx_data, 8'h00};
                shift_tx <= {tx_data, 8'h00};
            end else begin
                // CS active: SPI transfer in progress
                if (sck_rising) begin
                    // Sample MOSI on rising edge
                    shift_rx <= {shift_rx[14:0], mosi_sync[1]};
                    bit_cnt <= bit_cnt + 1;
                    
                    // After 16 bits, output received data
                    if (bit_cnt == 15) begin
                        rx_data <= {shift_rx[6:0], mosi_sync[1]};
                        rx_valid <= 1;
                        bit_cnt <= 0;
                    end
                end
                
                if (sck_falling) begin
                    // Output MISO on falling edge
                    miso <= shift_tx[15];
                    shift_tx <= {shift_tx[14:0], 1'b0};
                end
            end
        end
    end

endmodule